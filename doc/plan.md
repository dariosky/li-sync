# LimSync - Current Plan Snapshot

## Context and Constraints
- Goal: interactive, safe bidirectional sync between two potentially diverged trees.
- Endpoints are generic: both sides can be local or remote.
- Endpoint examples (illustrative):
  - `local:/path/to/folder`
  - `ssh://user@host/path/to/folder`
  - `user@host:~/path/to/folder`
- First-run safety is strict: no destructive defaults.
- Owner/group mismatches are informational only.

## Implemented Product Decisions
1. Endpoint model
- CLI uses `source` and `destination` endpoint inputs.
- Both endpoint formats are supported (typed URI + legacy remote syntax).
- Scan/apply can run for local-local, local-remote, remote-local, and remote-remote.

2. CLI surface
- Default command runs scan (no `scan` subcommand).
- Main invocation: `limsync --source ... --destination ...`.
- `review` remains a subcommand.

3. Safety
- Review-first workflow remains the default.
- Apply still requires explicit confirmation in TUI.
- Delete actions are not automatic.

4. UI terminology
- TUI keeps `left/right` language for actions and file sides.
- Endpoint abstraction is internal; interaction model stays familiar.

## Current Architecture

### Core modules (actual package)
- `src/limsync/endpoints.py`
  - Parses endpoint syntax and provides canonical endpoint specs.
  - Computes default per-endpoint state DB path and default review DB path.
- `src/limsync/scanner_local.py`
  - Local recursive scan with exclusions and nested `.dropboxignore`.
- `src/limsync/scanner_remote.py` + `src/limsync/remote_helper.py`
  - Remote scan via streamed SSH helper JSONL.
- `src/limsync/compare.py`
  - Content and metadata states tracked separately.
- `src/limsync/planner_apply.py`
  - Planner operation mapping and endpoint-aware apply execution.
- `src/limsync/state_db.py`
  - Single current workspace state + action overrides + UI prefs.
- `src/limsync/review_tui.py` + `src/limsync/review_actions.py` + `src/limsync/modals.py`
  - Interactive review, subtree operations, diff/open, apply flow.

### Interfaces
- CLI:
  - `limsync --source ... --destination ... [--state-db ...] [--open-review/--no-open-review]`
  - `limsync review [--state-db ...]`
- TUI:
  - Left/right action model, scoped update, plan view, apply confirmation.

### Transport
- SSH + SFTP for remote operations.
- Remote-to-remote apply is supported using local temp staging when needed.

## Persistence Model
- Per-endpoint scan snapshot DB defaults:
  - local endpoint: `<local_root>/.limsync/state.sqlite3`
  - remote endpoint: `<remote_root>/.limsync/state.sqlite3`
- Local review/worktree DB default:
  - `~/.limsync/<source_slug>__<destination_slug>.sqlite3`
- State context persists `source_endpoint` and `destination_endpoint` with compatibility for older DB rows.

## Data Model (High-level)
- Per path:
  - `content_state`: `identical | different | only_local | only_remote | unknown`
  - `metadata_state`: `identical | different | not_applicable`
  - `metadata_diff` + detailed metadata annotations
  - `recommended_action` and optional user override

## Exclusions
- Always excluded:
  - `.DS_Store`
  - `Icon\r`
- Excluded folders:
  - `CACHE_FOLDERS = {"__pycache__", ".pytest_cache", ".cache", ".ruff_cache"}`
  - `EXCLUDED_FOLDERS = {"node_modules", ".tox", ".venv", ".limsync"} | CACHE_FOLDERS`
- Nested `.dropboxignore` is respected.
- Xattr exclusion is intentionally disabled for performance.

## Testing Status and Priorities
- Current automated status: unit tests pass (`pytest`).
- Priorities:
  1. Exclusion correctness (`.dropboxignore`, excluded dirs/files).
  2. Compare correctness for content vs metadata-only drift.
  3. Planner/apply correctness for all endpoint combinations.
  4. Integration reliability over SSH helpers.

## Next Hardening Steps
1. Add dedicated tests for endpoint parsing variants and default DB path behavior.
2. Add integration coverage for remote-remote apply with larger file sets.
3. Add migration tests for old state DB schemas.
4. Improve docs for endpoint syntax edge cases (`ssh://.../~/path` handling).
