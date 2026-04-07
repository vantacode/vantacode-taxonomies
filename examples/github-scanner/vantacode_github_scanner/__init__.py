"""GitHub-wide VantaCode scanner.

Drives `gh search code` from the `github_search` field on rules in
`scanner-rules/`. Emits findings as JSON, CSV, or STIX 2.1.

Modules
-------
- gh        : thin wrapper around the gh CLI with rate-limit backoff
- scanner   : iterates rules + queries, calls gh, builds Findings
- output    : JSON / CSV / STIX 2.1 writers
- cli       : click entry point (`vantacode-gh-scan`)
"""

__version__ = "0.1.0"
