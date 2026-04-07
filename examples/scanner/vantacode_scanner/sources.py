"""Source resolution: local directory or remote GitHub repository.

`resolve_source` returns a (path, cleanup_callback) pair so the caller can
treat both modes uniformly. Cloning happens via the `git` binary on PATH —
no third-party Git library, no auth juggling.
"""

from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Callable
from urllib.parse import urlparse


def _looks_like_github(s: str) -> bool:
    if s.startswith(("http://", "https://", "git@")):
        return True
    return s.count("/") == 1 and not Path(s).exists()


def _normalize_github(s: str) -> str:
    if s.startswith("git@"):
        return s
    if s.startswith(("http://", "https://")):
        return s
    # owner/repo shorthand
    return f"https://github.com/{s}.git"


def resolve_source(source: str, *, depth: int = 1) -> tuple[Path, Callable[[], None]]:
    """Return (path, cleanup) for the given source.

    `source` may be a local directory or a GitHub URL / shorthand.
    """
    p = Path(source).expanduser()
    if p.exists() and p.is_dir():
        return p.resolve(), lambda: None

    if not _looks_like_github(source):
        raise ValueError(f"source not found and does not look like a git repo: {source}")

    url = _normalize_github(source)
    tmp = Path(tempfile.mkdtemp(prefix="vcs-scan-"))
    try:
        subprocess.run(
            ["git", "clone", "--depth", str(depth), "--quiet", url, str(tmp)],
            check=True,
        )
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        shutil.rmtree(tmp, ignore_errors=True)
        raise RuntimeError(f"git clone failed for {url}: {e}") from e

    def cleanup() -> None:
        shutil.rmtree(tmp, ignore_errors=True)

    return tmp, cleanup


def display_source(source: str) -> str:
    p = Path(source)
    if p.exists():
        return str(p.resolve())
    parsed = urlparse(source if "://" in source else f"https://github.com/{source}")
    return f"{parsed.scheme or 'https'}://{parsed.netloc or 'github.com'}{parsed.path}"
