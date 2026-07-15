"""Statistics panel for the Excel Automation Toolkit.

Displays processing results and dataframe statistics in a compact,
single-row label/value layout grouped into two sections.
"""

from typing import Any

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)


class _StatRow(QWidget):
    """A compact single-line label/value row for the statistics panel.

    Label is left-aligned in muted grey; value is right-aligned in bright
    white.  The entire row sits in ~22 px of vertical space.
    """

    def __init__(self, label: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 2, 8, 2)
        layout.setSpacing(4)

        self._label_widget = QLabel(label)
        self._label_widget.setStyleSheet("font-size: 10px; color: #7a7a8a;")
        self._label_widget.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred
        )

        self._value_widget = QLabel("—")
        self._value_widget.setStyleSheet(
            "font-size: 10px; color: #d8d8e8; font-weight: 600;"
        )
        self._value_widget.setAlignment(Qt.AlignmentFlag.AlignRight)
        self._value_widget.setFixedWidth(64)

        layout.addWidget(self._label_widget)
        layout.addWidget(self._value_widget)

    def set_value(self, value: str) -> None:
        self._value_widget.setText(value)


def _section_label(text: str) -> QLabel:
    """Return a small uppercase section-header label."""
    lbl = QLabel(text)
    lbl.setContentsMargins(8, 4, 8, 2)
    lbl.setStyleSheet(
        "font-size: 9px; color: #4a4a6a; font-weight: 700; letter-spacing: 1px;"
    )
    return lbl


def _divider() -> QFrame:
    """Return a 1-px horizontal separator."""
    line = QFrame()
    line.setFrameShape(QFrame.Shape.HLine)
    line.setContentsMargins(8, 0, 8, 0)
    line.setStyleSheet("color: #252535;")
    line.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
    return line


class StatisticsPanel(QGroupBox):
    """Compact statistics panel with two labelled sections.

    Sections
    --------
    DATA CLEANING  — row counts before/after cleanup
    WORKBOOK INFO  — column types, missing cells, memory
    """

    def __init__(self) -> None:
        super().__init__("Statistics")
        self.setObjectName("statisticsPanel")
        self._build_ui()

    def _build_ui(self) -> None:
        """Build the compact statistics layout."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 6, 0, 6)
        layout.setSpacing(0)

        # ── DATA CLEANING ────────────────────────────────────────────────
        layout.addWidget(_section_label("DATA CLEANING"))

        self.original_rows_value = _StatRow("Original Rows")
        self.current_rows_value = _StatRow("Current Rows")
        self.removed_empty_rows_value = _StatRow("Removed Empty")
        self.removed_duplicate_rows_value = _StatRow("Removed Duplicates")

        for row in (
            self.original_rows_value,
            self.current_rows_value,
            self.removed_empty_rows_value,
            self.removed_duplicate_rows_value,
        ):
            layout.addWidget(row)

        layout.addWidget(_divider())

        # ── WORKBOOK INFO ────────────────────────────────────────────────
        layout.addWidget(_section_label("WORKBOOK INFO"))

        self.columns_value = _StatRow("Columns")
        self.numeric_columns_value = _StatRow("Numeric")
        self.text_columns_value = _StatRow("Text")
        self.missing_cells_value = _StatRow("Missing Cells")
        self.memory_usage_value = _StatRow("Memory")

        for row in (
            self.columns_value,
            self.numeric_columns_value,
            self.text_columns_value,
            self.missing_cells_value,
            self.memory_usage_value,
        ):
            layout.addWidget(row)

        layout.addStretch()

    def update_statistics(
        self,
        processor_summary: dict[str, Any],
        stats_summary: dict[str, Any],
    ) -> None:
        """Update all displayed values from processing and statistics summaries."""
        self.original_rows_value.set_value(str(processor_summary["original_rows"]))
        self.current_rows_value.set_value(str(processor_summary["current_rows"]))
        self.removed_empty_rows_value.set_value(
            str(processor_summary["removed_empty_rows"])
        )
        self.removed_duplicate_rows_value.set_value(
            str(processor_summary["removed_duplicates"])
        )
        self.columns_value.set_value(str(stats_summary["columns"]))
        self.numeric_columns_value.set_value(str(stats_summary["numeric_columns"]))
        self.text_columns_value.set_value(str(stats_summary["text_columns"]))
        self.missing_cells_value.set_value(str(stats_summary["missing_cells"]))
        self.memory_usage_value.set_value(str(stats_summary["memory_usage"]))
