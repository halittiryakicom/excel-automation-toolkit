from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.figure import Figure


class ChartGenerator:
    """Generate reusable PNG charts from a pandas DataFrame."""

    def __init__(self, dataframe: pd.DataFrame) -> None:
        """Initialize the chart generator.

        Args:
            dataframe: Source dataframe used to generate charts.
        """
        self.df = dataframe

    def generate_all(self, output_folder: str | Path) -> list[Path]:
        """Generate all available charts.

        Args:
            output_folder: Base output folder. Charts are saved in its
                ``charts`` subfolder.

        Returns:
            Paths to the generated chart files.
        """
        return [
            self.generate_missing_values_chart(output_folder),
            self.generate_column_types_chart(output_folder),
            self.generate_numeric_distribution(output_folder),
        ]

    def generate_missing_values_chart(self, output_folder: str | Path) -> Path:
        """Generate a bar chart showing missing values per column.

        Args:
            output_folder: Base output folder.

        Returns:
            Path to the saved PNG chart.
        """
        chart_path = self._get_charts_folder(output_folder) / "missing_values.png"
        missing_values = self.df.isna().sum()

        fig, ax = plt.subplots(figsize=(10, 6))
        missing_values.plot(kind="bar", ax=ax, color="#4C78A8")

        ax.set_title("Missing Values by Column")
        ax.set_xlabel("Columns")
        ax.set_ylabel("Missing Cells")
        ax.tick_params(axis="x", rotation=45)
        fig.tight_layout()

        self._save_figure(fig, chart_path)
        return chart_path

    def generate_column_types_chart(self, output_folder: str | Path) -> Path:
        """Generate a chart showing numeric and text column counts.

        Args:
            output_folder: Base output folder.

        Returns:
            Path to the saved PNG chart.
        """
        chart_path = self._get_charts_folder(output_folder) / "column_types.png"
        numeric_count = len(self.df.select_dtypes(include="number").columns)
        text_count = len(self.df.select_dtypes(exclude="number").columns)

        fig, ax = plt.subplots(figsize=(7, 5))
        ax.bar(
            ["Numeric Columns", "Text Columns"],
            [numeric_count, text_count],
            color=["#54A24B", "#F58518"],
        )

        ax.set_title("Column Types")
        ax.set_ylabel("Column Count")
        fig.tight_layout()

        self._save_figure(fig, chart_path)
        return chart_path

    def generate_numeric_distribution(self, output_folder: str | Path) -> Path:
        """Generate histograms for numeric dataframe columns.

        Args:
            output_folder: Base output folder.

        Returns:
            Path to the saved PNG chart.
        """
        chart_path = self._get_charts_folder(output_folder) / "numeric_distribution.png"
        numeric_df = self.df.select_dtypes(include="number")

        if numeric_df.empty:
            fig, ax = plt.subplots(figsize=(8, 5))
            ax.text(
                0.5,
                0.5,
                "No numeric columns available",
                ha="center",
                va="center",
                fontsize=12,
            )
            ax.set_axis_off()
        else:
            numeric_df.hist(figsize=(10, 6), bins=20, color="#72B7B2")
            fig = plt.gcf()
            fig.suptitle("Numeric Column Distribution")
            fig.tight_layout()

        self._save_figure(fig, chart_path)
        return chart_path

    def _get_charts_folder(self, output_folder: str | Path) -> Path:
        """Create and return the charts output folder."""
        charts_folder = Path(output_folder) / "charts"
        charts_folder.mkdir(parents=True, exist_ok=True)
        return charts_folder

    def _save_figure(self, figure: Figure, chart_path: Path) -> None:
        """Save a matplotlib figure and close it."""
        figure.savefig(chart_path, format="png", dpi=150)
        plt.close(figure)
