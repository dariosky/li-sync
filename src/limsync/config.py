from __future__ import annotations

from dataclasses import dataclass

CACHE_FOLDERS = {"__pycache__", ".pytest_cache", ".cache", ".ruff_cache"}
EXCLUDED_FOLDERS = {"node_modules", ".tox", ".venv", ".limsync"} | CACHE_FOLDERS
EXCLUDED_FILE_NAMES = {".DS_Store", "Icon\r"}

DEFAULT_REMOTE_PORT = 22
DEFAULT_STATE_SUBPATH = ".limsync/state.sqlite3"


@dataclass(frozen=True)
class RemoteConfig:
    host: str
    user: str
    port: int = DEFAULT_REMOTE_PORT
    root: str = "."
    state_db: str = DEFAULT_STATE_SUBPATH

    @property
    def address(self) -> str:
        port_part = "" if self.port == DEFAULT_REMOTE_PORT else f":{self.port}"
        return f"{self.user}@{self.host}{port_part}:{self.root}"
