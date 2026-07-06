from pathlib import Path
from typing import Optional

import pandas as pd


class ExcelProcessor:
    """
    Handles all Excel processing operations.
    """

    def __init__(self) -> None:
        self.df: Optional[pd.DataFrame] = None

        # Statistics
        self.original_rows: int = 0
        self.current_rows: int = 0
        self.removed_empty_rows: int = 0
        self.removed_duplicates: int = 0

    def load_excel(self, file_path: str | Path) -> None:
        """
        Load an Excel file into memory.
        """

        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        self.df = pd.read_excel(file_path)

        self.original_rows = len(self.df)
        self.current_rows = len(self.df)

    def remove_empty_rows(self) -> None:
        """
        Remove rows containing only empty values.
        """

        self._ensure_dataframe()

        before = len(self.df)

        self.df = self.df.dropna(how="all")

        after = len(self.df)

        self.removed_empty_rows = before - after
        self.current_rows = after

    def remove_duplicates(self) -> None:
        """
        Remove duplicate rows.
        """

        self._ensure_dataframe()

        before = len(self.df)

        self.df = self.df.drop_duplicates()

        after = len(self.df)

        self.removed_duplicates = before - after
        self.current_rows = after

    def save_excel(self, output_path: str | Path) -> Path:
        """
        Save processed dataframe.
        """

        self._ensure_dataframe()

        output_path = Path(output_path)

        output_path.parent.mkdir(parents=True, exist_ok=True)

        self.df.to_excel(
            output_path,
            index=False,
            engine="openpyxl",
        )

        return output_path

    def get_summary(self) -> dict:
        """
        Return processing summary.
        """

        return {
            "original_rows": self.original_rows,
            "current_rows": self.current_rows,
            "removed_empty_rows": self.removed_empty_rows,
            "removed_duplicates": self.removed_duplicates,
        }

    def reset(self) -> None:
        """
        Reset processor state.
        """

        self.df = None

        self.original_rows = 0
        self.current_rows = 0
        self.removed_empty_rows = 0
        self.removed_duplicates = 0

    def _ensure_dataframe(self) -> None:
        """
        Ensure dataframe exists before processing.
        """

        if self.df is None:
            raise RuntimeError("No Excel file loaded.")