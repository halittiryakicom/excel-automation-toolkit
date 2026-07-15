"""Persistent user preferences manager using QSettings."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QSettings

# Keys used in QSettings storage
_KEY_LAST_FOLDER = "file/last_folder"


class SettingsManager:
    """Manage persistent application preferences with QSettings.

    Wraps QSettings to provide a clean, typed interface for reading
    and writing application-level preferences.
    """

    def __init__(self) -> None:
        # Uses the INI format so values are stored in a human-readable file
        # under the OS-appropriate user config location.
        self._settings = QSettings("HalitTiryaki", "ExcelAutomationToolkit")

    # ------------------------------------------------------------------
    # Last-used folder
    # ------------------------------------------------------------------

    def get_last_folder(self) -> str:
        """Return the last folder the user opened a file from.

        Falls back to the user's Documents directory when:
        - no folder has been stored yet, or
        - the stored folder no longer exists on disk.
        """
        stored: str = self._settings.value(_KEY_LAST_FOLDER, "")

        if stored and Path(stored).is_dir():
            return stored

        # Fallback: standard Documents directory
        return str(Path.home() / "Documents")

    def set_last_folder(self, folder_path: str | Path) -> None:
        """Persist the last-used folder path.

        Args:
            folder_path: The directory that should be remembered.
        """
        self._settings.setValue(_KEY_LAST_FOLDER, str(folder_path))
        self._settings.sync()
