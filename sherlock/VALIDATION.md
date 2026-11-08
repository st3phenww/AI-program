# Validation record

Date: 2026-11-08, Australia/Sydney.

Environment: Linux, Python 3.12.14, original PyPI package `sherlock-project==0.16.2`.

## Checks completed

- `sherlock --version`: returned `Sherlock v0.16.2`.
- `uv pip check`: all 18 installed packages compatible.
- Live lookup through `run.py`, limited to GitHub and using the release's bundled rules:

  ```bash
  .venv/bin/python run.py sherlock-project sherlock-test-82d4f9bc --site GitHub --frozen-sites --timeout 15
  ```

| Test input | Actual upstream result | HTTP status |
| --- | --- | --- |
| `sherlock-project` (the public upstream organization) | Claimed | 200 |
| `sherlock-test-82d4f9bc` (random test name) | Available | 404 |

The combined run exited with code 0, exported both CSV rows and TXT files, and generated an HTML report plus run metadata. These are observations at test time; the random test name is not guaranteed to remain unregistered.

Launcher checks confirmed that path-like or option-like usernames are rejected, HTML text is escaped, non-HTTP links are not rendered, and Unknown and Available remain distinct. These checks used synthetic records and did not query personal accounts.

## Limits of verification

- Windows and macOS launchers were prepared but not executed on those operating systems.
- The HTML output was inspected programmatically; no browser visual QA was completed.
- The live network test used GitHub only. Other sites may impose rate limits or block cloud IPs.
- Default online catalogue/exclusion refresh was not part of this reproducible smoke test.
- No always-on public server or browser API was deployed. The validated installation is an on-demand cloud session environment.
- No local user computer was accessed or modified.
