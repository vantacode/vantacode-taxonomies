"""Thin wrapper around the `gh` CLI for GitHub Code Search.

Why a wrapper instead of calling the GitHub REST API directly:

- `gh` already handles auth (via `gh auth login`), so the user gets the
  authenticated rate limit (30 req/min for code search) for free.
- `gh search code` returns results as JSON via `--json`, which is stable
  across versions.
- The legacy code-search API used by `gh` caps total results at 1000
  regardless of paging, so we map `pages * per_page → --limit`.

The one nontrivial gotcha: `gh search code` parses positional args as the
query. If you pass the entire query as a single argv element containing
spaces, gh wraps the whole thing in outer quotes and searches for one
literal phrase. We `shlex.split` here so each quoted phrase / bare token
becomes its own argv element and GitHub treats them as an AND-group.
"""

from __future__ import annotations

import json
import shlex
import shutil
import subprocess
import time
from dataclasses import dataclass
from typing import Any


GH_BIN = "gh"

# Auth-aware safe defaults. GitHub allows 30 code-search requests per minute
# for authenticated users, 10 per minute unauthenticated. Stay well under.
DEFAULT_PAUSE_SECONDS = 2.5

# Hard cap on `gh search code` total results. The legacy API maxes at 1000.
MAX_LIMIT = 1000


@dataclass
class GhHit:
    repo: str
    path: str
    url: str
    fragments: list[str]


def gh_available() -> bool:
    return shutil.which(GH_BIN) is not None


def gh_authenticated() -> tuple[bool, str]:
    """Return (is_authenticated, status_message)."""
    if not gh_available():
        return False, f"{GH_BIN} CLI not found on PATH"
    try:
        r = subprocess.run(
            [GH_BIN, "auth", "status"],
            capture_output=True, text=True, timeout=10,
        )
    except (subprocess.TimeoutExpired, FileNotFoundError) as e:
        return False, f"gh auth status failed: {e}"
    # gh writes auth info to stderr regardless of state
    out = (r.stderr or "") + (r.stdout or "")
    if r.returncode != 0:
        return False, out.strip() or "gh auth status returned non-zero"
    return True, out.strip()


def _run_gh(args: list[str], timeout: int = 120) -> tuple[str, str, int]:
    try:
        r = subprocess.run(
            [GH_BIN] + args,
            capture_output=True, text=True, timeout=timeout,
        )
        return r.stdout or "", r.stderr or "", r.returncode
    except FileNotFoundError:
        return "", f"{GH_BIN} CLI not found", 127
    except subprocess.TimeoutExpired:
        return "", "timeout", 124


def search_code(
    query: str,
    *,
    language: str | None = None,
    pages: int = 1,
    per_page: int = 100,
    pause_seconds: float = DEFAULT_PAUSE_SECONDS,
    timeout: int = 120,
) -> tuple[list[GhHit], str | None]:
    """Run `gh search code <query> [--language <lang>]`.

    Returns `(hits, error_message)`. `hits` is empty when there are no
    results OR when an error occurred — check `error_message` to tell
    them apart.

    `query` is fed verbatim through shlex so quoted phrases stay grouped
    as the user wrote them.
    """
    limit = min(max(pages * per_page, 1), MAX_LIMIT)

    try:
        query_tokens = shlex.split(query)
    except ValueError:
        # fall back to single arg if the query has unbalanced quotes
        query_tokens = [query]

    args: list[str] = ["search", "code", *query_tokens,
                       "--limit", str(limit),
                       "--json", "path,repository,url,textMatches"]
    if language:
        args += ["--language", language]

    out, err, rc = _run_gh(args, timeout=timeout)

    # Rate-limit handling — back off and retry once
    err_lower = err.lower()
    if rc != 0 and ("rate limit" in err_lower or "403" in err or "429" in err):
        time.sleep(30)
        out, err, rc = _run_gh(args, timeout=timeout)

    if rc != 0:
        msg = err.strip() or f"gh exited with code {rc}"
        return [], msg

    # gh returns either a JSON array (one shot) or NDJSON depending on flags;
    # `--json path,repository,url,textMatches` without `--jq` returns an array.
    hits: list[GhHit] = []
    payload: Any
    text = out.strip()
    if not text:
        if pause_seconds:
            time.sleep(pause_seconds)
        return hits, None
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as e:
        return [], f"failed to parse gh JSON output: {e}"

    if isinstance(payload, dict):
        payload = [payload]

    for item in payload or []:
        repo_obj = item.get("repository") or {}
        repo_name = repo_obj.get("nameWithOwner") or repo_obj.get("full_name") or ""
        path = item.get("path") or ""
        url = item.get("url") or (
            f"https://github.com/{repo_name}/blob/HEAD/{path}" if repo_name and path else ""
        )
        frags: list[str] = []
        for tm in item.get("textMatches") or []:
            frag = tm.get("fragment")
            if isinstance(frag, str) and frag:
                frags.append(frag.strip())
        hits.append(GhHit(repo=repo_name, path=path, url=url, fragments=frags))

    if pause_seconds:
        time.sleep(pause_seconds)

    return hits, None
