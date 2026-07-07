from typing import Any

from PySide6.QtWidgets import QFormLayout, QGroupBox, QLabel


class StatisticsPanel(QGroupBox):
    """Reusable panel for displaying processing and dataframe statistics."""

    def __init__(self) -> None:
        """Initialize the statistics panel."""
        super().__init__("Statistics")
        self._build_ui()

    def _build_ui(self) -> None:
        """Build the statistics labels and layout."""
        layout = QFormLayout()

        self.original_rows_value = QLabel("-")
        self.current_rows_value = QLabel("-")
        self.removed_empty_rows_value = QLabel("-")
        self.removed_duplicate_rows_value = QLabel("-")
        self.columns_value = QLabel("-")
        self.numeric_columns_value = QLabel("-")
        self.text_columns_value = QLabel("-")
        self.missing_cells_value = QLabel("-")
        self.memory_usage_value = QLabel("-")

        layout.addRow("Original Rows", self.original_rows_value)
        layout.addRow("Current Rows", self.current_rows_value)
        layout.addRow("Removed Empty Rows", self.removed_empty_rows_value)
        layout.addRow("Removed Duplicate Rows", self.removed_duplicate_rows_value)
        layout.addRow("Columns", self.columns_value)
        layout.addRow("Numeric Columns", self.numeric_columns_value)
        layout.addRow("Text Columns", self.text_columns_value)
        layout.addRow("Missing Cells", self.missing_cells_value)
        layout.addRow("Memory Usage", self.memory_usage_value)

        self.setLayout(layout)

    def update_statistics(
        self,
        processor_summary: dict[str, Any],
        stats_summary: dict[str, Any],
    ) -> None:
        """Update displayed values from processing and statistics summaries."""
        self.original_rows_value.setText(str(processor_summary["original_rows"]))
        self.current_rows_value.setText(str(processor_summary["current_rows"]))
        self.removed_empty_rows_value.setText(
            str(processor_summary["removed_empty_rows"])
        )
        self.removed_duplicate_rows_value.setText(
            str(processor_summary["removed_duplicates"])
        )
        self.columns_value.setText(str(stats_summary["columns"]))
        self.numeric_columns_value.setText(str(stats_summary["numeric_columns"]))
        self.text_columns_value.setText(str(stats_summary["text_columns"]))
        self.missing_cells_value.setText(str(stats_summary["missing_cells"]))
        self.memory_usage_value.setText(str(stats_summary["memory_usage"]))
