"""Persistence for recently opened Excel files."""

from __future__ import annotations

import json
from pathlib import Path


class RecentFilesManager:
    """Manage recently opened Excel files with JSON persistence."""

    def __init__(self, storage_path: Path | None = None, max_files: int = 5) -> None:
        self.max_files = max_files
        self.storage_path = storage_path or self._default_storage_path()
        self._recent_files = self._load_recent_files()

    def _default_storage_path(self) -> Path:
        """Return the default JSON storage path."""
        project_root = Path(__file__).resolve().parents[1]
        return project_root / "config" / "recent_files.json"

    def _normalize_path(self, file_path: str | Path) -> str:
        """Normalize a file path for storage and duplicate checks."""
        return Path(file_path).expanduser().resolve(strict=False).as_posix()

    def _path_key(self, file_path: str | Path) -> str:
        """Return a comparable key for duplicate detection."""
        return self._normalize_path(file_path).casefold()

    def _ensure_storage_file(self) -> None:
        """Create the storage file if it does not exist."""
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.storage_path.exists():
            self._write_recent_files([])

    def _read_storage(self) -> list[str]:
        """Read recent files from disk."""
        self._ensure_storage_file()

        try:
            with self.storage_path.open("r", encoding="utf-8") as file_handle:
                payload = json.load(file_handle)
        except (OSError, json.JSONDecodeError):
            return []

        recent_files = payload.get("recent_files", [])
        if not isinstance(recent_files, list):
            return []

        return [str(item) for item in recent_files]

    def _write_recent_files(self, recent_files: list[str]) -> None:
        """Persist the recent files list to disk."""
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {"recent_files": recent_files[: self.max_files]}

        with self.storage_path.open("w", encoding="utf-8") as file_handle:
            json.dump(payload, file_handle, indent=4)

    def _clean_recent_files(self, recent_files: list[str]) -> list[str]:
        """Remove duplicates, trim to max files, and drop missing files."""
        cleaned_files: list[str] = []
        seen_paths: set[str] = set()

        for file_path in recent_files:
            normalized_path = self._normalize_path(file_path)
            path_key = normalized_path.casefold()

            if path_key in seen_paths:
                continue

            if not Path(normalized_path).exists():
                continue

            seen_paths.add(path_key)
            cleaned_files.append(normalized_path)

            if len(cleaned_files) >= self.max_files:
                break

        return cleaned_files

    def _load_recent_files(self) -> list[str]:
        """Load and sanitize the persisted recent files list."""
        recent_files = self._clean_recent_files(self._read_storage())
        self._write_recent_files(recent_files)
        return recent_files

    def get_recent_files(self) -> list[str]:
        """Return the current recent files list."""
        self._recent_files = self._clean_recent_files(self._recent_files)
        self._write_recent_files(self._recent_files)
        return list(self._recent_files)

    def add_file(self, file_path: str | Path) -> list[str]:
        """Add a file to the top of the recent list."""
        normalized_path = self._normalize_path(file_path)
        path_key = self._path_key(normalized_path)

        if not Path(normalized_path).exists():
            return self.get_recent_files()

        updated_files = [
            existing_path
            for existing_path in self.get_recent_files()
            if self._path_key(existing_path) != path_key
        ]
        updated_files.insert(0, normalized_path)

        self._recent_files = self._clean_recent_files(updated_files)
        self._write_recent_files(self._recent_files)
        return list(self._recent_files)

    def remove_file(self, file_path: str | Path) -> list[str]:
        """Remove a file from the recent list if present."""
        normalized_path = self._normalize_path(file_path)
        path_key = self._path_key(normalized_path)
        self._recent_files = [
            existing_path
            for existing_path in self.get_recent_files()
            if self._path_key(existing_path) != path_key
        ]
        self._write_recent_files(self._recent_files)
        return list(self._recent_files)
