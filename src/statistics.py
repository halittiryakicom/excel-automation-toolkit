from typing import Any

import pandas as pd


class StatisticsEngine:
    """
    Generates statistical information from a pandas DataFrame.

    This class never modifies the DataFrame.
    It only analyzes the data.
    """

    def __init__(self, dataframe: pd.DataFrame) -> None:
        self.df = dataframe

    def generate_summary(self) -> dict[str, Any]:
        """
        Generate a general summary of the dataframe.
        """

        return {
            "rows": self.get_row_count(),
            "columns": self.get_column_count(),
            "numeric_columns": self.get_numeric_column_count(),
            "text_columns": self.get_text_column_count(),
            "missing_cells": self.get_missing_cell_count(),
            "memory_usage": self.get_memory_usage(),
            "column_names": self.get_column_names(),
        }

    # ---------------------------------------------------------
    # Basic Information
    # ---------------------------------------------------------

    def get_row_count(self) -> int:
        return len(self.df)

    def get_column_count(self) -> int:
        return len(self.df.columns)

    def get_column_names(self) -> list[str]:
        return self.df.columns.tolist()

    # ---------------------------------------------------------
    # Column Types
    # ---------------------------------------------------------

    def get_numeric_dataframe(self) -> pd.DataFrame:
        return self.df.select_dtypes(include="number")

    def get_text_dataframe(self) -> pd.DataFrame:
        return self.df.select_dtypes(exclude="number")

    def get_numeric_column_count(self) -> int:
        return len(self.get_numeric_dataframe().columns)

    def get_text_column_count(self) -> int:
        return len(self.get_text_dataframe().columns)

    # ---------------------------------------------------------
    # Missing Data
    # ---------------------------------------------------------

    def get_missing_cell_count(self) -> int:
        return int(self.df.isna().sum().sum())

    # ---------------------------------------------------------
    # Memory
    # ---------------------------------------------------------

    def get_memory_usage(self) -> str:
        memory = self.df.memory_usage(deep=True).sum()

        if memory < 1024:
            return f"{memory} Bytes"

        if memory < 1024 * 1024:
            return f"{memory / 1024:.2f} KB"

        return f"{memory / (1024 * 1024):.2f} MB"

    # ---------------------------------------------------------
    # Numeric Statistics
    # ---------------------------------------------------------

    def calculate_mean(self) -> pd.Series:
        return self.get_numeric_dataframe().mean()

    def calculate_sum(self) -> pd.Series:
        return self.get_numeric_dataframe().sum()

    def calculate_min(self) -> pd.Series:
        return self.get_numeric_dataframe().min()

    def calculate_max(self) -> pd.Series:
        return self.get_numeric_dataframe().max()

    def calculate_median(self) -> pd.Series:
        return self.get_numeric_dataframe().median()

    def calculate_std(self) -> pd.Series:
        return self.get_numeric_dataframe().std()