"""Main application window for the Excel Automation Toolkit."""

import os
from pathlib import Path

from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import (
    QAction,
    QDragEnterEvent,
    QDragLeaveEvent,
    QDropEvent,
    QResizeEvent,
)
from PySide6.QtWidgets import (
    QAbstractItemView,
    QCheckBox,
    QFileDialog,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMenu,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QSizePolicy,
    QStatusBar,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from src.core.charts import ChartGenerator
from src.core.excel_processor import ExcelProcessor
from src.core.statistics import StatisticsEngine
from src.gui.drop_overlay import DropOverlay
from src.gui.statistics_panel import StatisticsPanel
from services.recent_files_manager import RecentFilesManager
from services.settings_manager import SettingsManager

# Application version shown in the status bar and About dialog
_VERSION = "1.2.1"


class MainWindow(QMainWindow):
    """Main window for the Excel Automation Toolkit."""

    # Accepted Excel file extensions for drag & drop and browse validation
    _ACCEPTED_EXTENSIONS: frozenset[str] = frozenset({".xlsx", ".xls"})

    def __init__(self) -> None:
        """Initialize the main application window."""
        super().__init__()

        self.setWindowTitle("Excel Automation Toolkit")
        self.resize(900, 640)

        self.file_path = ""
        self.generated_chart_paths: list[Path] = []
        self.recent_files_manager = RecentFilesManager()
        self.settings_manager = SettingsManager()

        # Enable the window to receive drag & drop events
        self.setAcceptDrops(True)

        self.setup_ui()
        self._build_status_bar()
        self._build_menu_bar()
        self.refresh_recent_files()

        # Overlay is parented to the central widget so it fills only the
        # content area (not the menu bar / status bar).
        self._drop_overlay = DropOverlay(self.centralWidget())

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def setup_ui(self) -> None:
        """Build the main application interface."""
        central = QWidget()
        self.setCentralWidget(central)

        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(8)

        main_layout.addWidget(self._build_file_section())
        main_layout.addWidget(self._build_recent_files_group())

        # Middle row: Operations | Output Folder (side by side)
        middle_row = QHBoxLayout()
        middle_row.setSpacing(8)
        middle_row.addWidget(self._build_operations_group(), 1)
        middle_row.addWidget(self._build_output_folder_group(), 1)
        main_layout.addLayout(middle_row)

        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setFixedHeight(6)
        self.progress_bar.setToolTip("Processing progress.")
        self.progress_bar.setTextVisible(False)
        main_layout.addWidget(self.progress_bar)

        main_layout.addLayout(self._build_results_layout(), stretch=1)
        main_layout.addWidget(self._build_process_button())

    # ── File selection section ─────────────────────────────────────────

    def _build_file_section(self) -> QGroupBox:
        """Create the file selection group with a clean filename display."""
        group = QGroupBox("Selected File")
        group.setToolTip("Excel file that will be processed.")
        layout = QHBoxLayout(group)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        # Icon + filename label (replaces the raw path line edit)
        self._file_icon_label = QLabel("📄")
        self._file_icon_label.setFixedWidth(22)
        self._file_icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.path_edit = QLabel("No file selected")
        self.path_edit.setObjectName("filePathLabel")
        self.path_edit.setToolTip("")
        self.path_edit.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred
        )
        self.path_edit.setStyleSheet("color: #888; font-style: italic;")

        browse_button = QPushButton("Browse…")
        browse_button.setFixedWidth(90)
        browse_button.setToolTip("Choose an Excel file to process.")
        browse_button.clicked.connect(self.browse_excel)

        layout.addWidget(self._file_icon_label)
        layout.addWidget(self.path_edit, stretch=1)
        layout.addWidget(browse_button)
        return group

    # ── Recent files ──────────────────────────────────────────────────

    def _build_recent_files_group(self) -> QGroupBox:
        """Create the recent files list with double-click and context menu."""
        group = QGroupBox("Recent Files")
        group.setToolTip("Quickly reopen recently used Excel files.")
        layout = QVBoxLayout(group)
        layout.setContentsMargins(6, 6, 6, 6)

        self.recent_files_list = QListWidget()
        self.recent_files_list.setFixedHeight(72)
        self.recent_files_list.setToolTip(
            "Double-click to open. Right-click for options."
        )
        self.recent_files_list.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )
        # Double-click loads the file
        self.recent_files_list.itemDoubleClicked.connect(self.open_recent_file)
        # Right-click context menu
        self.recent_files_list.setContextMenuPolicy(
            Qt.ContextMenuPolicy.CustomContextMenu
        )
        self.recent_files_list.customContextMenuRequested.connect(
            self._show_recent_files_context_menu
        )

        layout.addWidget(self.recent_files_list)
        return group

    def _show_recent_files_context_menu(self, pos) -> None:
        """Show a context menu for the recent files list."""
        item = self.recent_files_list.itemAt(pos)
        menu = QMenu(self)

        if item and item.data(Qt.ItemDataRole.UserRole):
            remove_action = menu.addAction("Remove")
            remove_action.triggered.connect(lambda: self._remove_recent_file(item))
            menu.addSeparator()

        clear_action = menu.addAction("Clear History")
        clear_action.triggered.connect(self._clear_recent_files)

        menu.exec(self.recent_files_list.mapToGlobal(pos))

    def _remove_recent_file(self, item: QListWidgetItem) -> None:
        """Remove a single entry from the recent files list."""
        file_path = item.data(Qt.ItemDataRole.UserRole)
        if file_path:
            self.recent_files_manager.remove_file(file_path)
            self.refresh_recent_files()

    def _clear_recent_files(self) -> None:
        """Clear the entire recent files history."""
        for file_path in self.recent_files_manager.get_recent_files():
            self.recent_files_manager.remove_file(file_path)
        self.refresh_recent_files()

    # ── Operations ────────────────────────────────────────────────────

    def _build_operations_group(self) -> QGroupBox:
        """Create the operations checkbox group with categorised sections."""
        group = QGroupBox("Operations")
        group.setToolTip("Select which operations to run.")
        layout = QVBoxLayout(group)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(4)

        # ── Cleaning category ────────────────────────────────────────
        layout.addWidget(self._make_category_label("Cleaning"))

        self.remove_empty_rows_checkbox = QCheckBox("Remove Empty Rows")
        self.remove_empty_rows_checkbox.setChecked(True)
        self.remove_empty_rows_checkbox.setToolTip(
            "Remove rows where every cell is empty."
        )

        self.remove_duplicate_rows_checkbox = QCheckBox("Remove Duplicate Rows")
        self.remove_duplicate_rows_checkbox.setChecked(True)
        self.remove_duplicate_rows_checkbox.setToolTip(
            "Remove rows that are exact duplicates."
        )

        layout.addWidget(self.remove_empty_rows_checkbox)
        layout.addWidget(self.remove_duplicate_rows_checkbox)

        layout.addWidget(self._make_section_divider())

        # ── Reports category ─────────────────────────────────────────
        layout.addWidget(self._make_category_label("Reports"))

        self.generate_statistics_checkbox = QCheckBox("Statistics")
        self.generate_statistics_checkbox.setToolTip(
            "Generate summary statistics for the processed data."
        )
        self.generate_charts_checkbox = QCheckBox("Charts")
        self.generate_charts_checkbox.setToolTip(
            "Generate chart images in the output charts folder."
        )
        self.generate_pdf_report_checkbox = QCheckBox("PDF Report")
        self.generate_pdf_report_checkbox.setToolTip(
            "Reserve report generation for PDF output."
        )

        layout.addWidget(self.generate_statistics_checkbox)
        layout.addWidget(self.generate_charts_checkbox)
        layout.addWidget(self.generate_pdf_report_checkbox)
        layout.addStretch()

        return group

    # ── Output folder ─────────────────────────────────────────────────

    def _build_output_folder_group(self) -> QGroupBox:
        """Create the output folder section with browse and open buttons."""
        group = QGroupBox("Output Folder")
        group.setToolTip("Folder where generated files are saved.")
        layout = QVBoxLayout(group)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)

        self.output_folder_edit = QLineEdit("output/")
        self.output_folder_edit.setReadOnly(True)
        self.output_folder_edit.setToolTip("Folder where generated files are saved.")
        layout.addWidget(self.output_folder_edit)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(6)

        browse_output_button = QPushButton("Browse")
        browse_output_button.setToolTip("Choose a different output folder.")
        browse_output_button.clicked.connect(self._browse_output_folder)

        self.open_output_folder_button = QPushButton("📂 Open Folder")
        self.open_output_folder_button.setToolTip("Open the configured output folder.")
        self.open_output_folder_button.clicked.connect(self.open_output_folder)

        btn_row.addWidget(browse_output_button)
        btn_row.addWidget(self.open_output_folder_button)
        layout.addLayout(btn_row)
        layout.addStretch()

        return group

    # ── Results (Log + Statistics) ────────────────────────────────────

    def _build_results_layout(self) -> QHBoxLayout:
        """Create the side-by-side log and statistics panels."""
        results_layout = QHBoxLayout()
        results_layout.setSpacing(8)

        log_group = QGroupBox("Log")
        log_layout = QVBoxLayout(log_group)
        log_layout.setContentsMargins(6, 6, 6, 6)

        self.log_box = QTextEdit()
        self.log_box.setReadOnly(True)
        self.log_box.setText("Application started.")
        self.log_box.setToolTip("Processing messages and results.")

        log_layout.addWidget(self.log_box)

        self.statistics_panel = StatisticsPanel()
        self.statistics_panel.setToolTip("Statistics for the processed workbook.")

        results_layout.addWidget(log_group, 2)
        results_layout.addWidget(self.statistics_panel, 1)

        return results_layout

    # ── Process button ────────────────────────────────────────────────

    def _build_process_button(self) -> QPushButton:
        """Create the main process action button."""
        self.process_button = QPushButton("🚀  Process Excel File")
        self.process_button.setFixedHeight(42)
        self.process_button.setToolTip("Run the selected Excel operations.")
        self.process_button.clicked.connect(self.process_excel)
        return self.process_button

    # ── Status bar ────────────────────────────────────────────────────

    def _build_status_bar(self) -> None:
        """Create the main window status bar with version indicator."""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        # Permanent right-hand version label
        version_label = QLabel(f"v{_VERSION}")
        version_label.setStyleSheet("color: #666; margin-right: 6px;")
        self.status_bar.addPermanentWidget(version_label)

        self.set_status("Ready")

    # ── Menu bar ──────────────────────────────────────────────────────

    def _build_menu_bar(self) -> None:
        """Create the application menu bar."""
        help_menu = self.menuBar().addMenu("Help")

        about_action = QAction("About", self)
        about_action.setStatusTip("About Excel Automation Toolkit")
        about_action.triggered.connect(self.show_about_dialog)

        help_menu.addAction(about_action)

    # ── Helper widgets ────────────────────────────────────────────────

    @staticmethod
    def _make_category_label(text: str) -> QLabel:
        """Return a styled uppercase category label for the operations group."""
        label = QLabel(text)
        label.setStyleSheet(
            "font-size: 9px; color: #5a5a7a; font-weight: 700; letter-spacing: 1px;"
        )
        return label

    @staticmethod
    def _make_section_divider() -> QFrame:
        """Return a thin horizontal line to divide operation categories."""
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet("color: #2a2a3a; margin: 2px 0;")
        return line

    # ------------------------------------------------------------------
    # About dialog
    # ------------------------------------------------------------------

    def show_about_dialog(self) -> None:
        """Display application information."""
        QMessageBox.about(
            self,
            "About Excel Automation Toolkit",
            (
                "<b>Excel Automation Toolkit</b><br>"
                f"Version {_VERSION}<br><br>"
                "Developer: Halit Tiryaki<br><br>"
                "<b>Technologies</b><br>"
                "Python<br>"
                "PySide6<br>"
                "Pandas<br>"
                "OpenPyXL<br>"
                "Matplotlib"
            ),
        )

    # ------------------------------------------------------------------
    # Drag & Drop
    # ------------------------------------------------------------------

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        """Accept the drag if it contains at least one valid Excel file URL."""
        if event.mimeData().hasUrls() and self._drag_contains_excel(
            event.mimeData().urls()
        ):
            event.acceptProposedAction()
            self._drop_overlay.show_overlay()
        else:
            event.ignore()

    def dragLeaveEvent(self, event: QDragLeaveEvent) -> None:
        """Hide the overlay when the drag leaves the window."""
        self._drop_overlay.hide_overlay()
        super().dragLeaveEvent(event)

    def dropEvent(self, event: QDropEvent) -> None:
        """Handle a file drop: validate the extension and load the first Excel file."""
        # Always dismiss the overlay immediately on drop regardless of validity
        self._drop_overlay.force_hide()

        urls: list[QUrl] = event.mimeData().urls()
        excel_urls = [url for url in urls if self._is_valid_excel_url(url)]

        if not excel_urls:
            self.log("Drop rejected: no valid Excel file (.xlsx / .xls) found.")
            self.set_status("Drop rejected — not a valid Excel file.")
            QMessageBox.warning(
                self,
                "Invalid File",
                "Please drop a valid Excel file (.xlsx or .xls).",
            )
            return

        # Use only the first valid file when multiple files are dropped
        file_path = excel_urls[0].toLocalFile()
        self.log(f"File dropped: {file_path}")
        self.set_status(f"File loaded via drag & drop: {Path(file_path).name}")
        self._set_selected_file(file_path)

    def _drag_contains_excel(self, urls: list[QUrl]) -> bool:
        """Return True if at least one URL points to a valid Excel file."""
        return any(self._is_valid_excel_url(url) for url in urls)

    def _is_valid_excel_url(self, url: QUrl) -> bool:
        """Return True if the URL is a local file with an accepted Excel extension."""
        if not url.isLocalFile():
            return False
        return Path(url.toLocalFile()).suffix.lower() in self._ACCEPTED_EXTENSIONS

    def resizeEvent(self, event: QResizeEvent) -> None:
        """Keep the drop overlay filling the central widget on every resize."""
        super().resizeEvent(event)
        self._drop_overlay.refit()

    # ------------------------------------------------------------------
    # File selection
    # ------------------------------------------------------------------

    def browse_excel(self) -> None:
        """Open a file dialog and store the selected Excel file path."""
        start_dir = self.settings_manager.get_last_folder()

        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "Select Excel File",
            start_dir,
            "Excel Files (*.xlsx *.xls)",
        )

        if file_name:
            self._set_selected_file(file_name)

    def _browse_output_folder(self) -> None:
        """Open a directory dialog to change the output folder."""
        folder = QFileDialog.getExistingDirectory(
            self,
            "Select Output Folder",
            self.output_folder_edit.text(),
        )
        if folder:
            self.output_folder_edit.setText(folder)

    def _set_selected_file(self, file_path: str | Path) -> None:
        """Set the active file path, persist it in recent files, and remember its folder."""
        normalized_path = Path(file_path).expanduser().resolve(strict=False)
        self.file_path = str(normalized_path)

        # Show only the filename in the label; full path lives in the tooltip
        self.path_edit.setText(normalized_path.name)
        self.path_edit.setToolTip(self.file_path)
        self.path_edit.setStyleSheet("color: #e8e8f0; font-style: normal; font-weight: 500;")

        self.recent_files_manager.add_file(self.file_path)
        self.refresh_recent_files()

        # Persist the parent directory so the next file dialog opens here
        self.settings_manager.set_last_folder(str(normalized_path.parent))

    # ------------------------------------------------------------------
    # Recent files
    # ------------------------------------------------------------------

    def refresh_recent_files(self) -> None:
        """Refresh the recent files list shown in the UI."""
        recent_files = self.recent_files_manager.get_recent_files()

        self.recent_files_list.clear()

        if not recent_files:
            empty_item = QListWidgetItem("No recent files")
            empty_item.setFlags(Qt.ItemFlag.NoItemFlags)
            self.recent_files_list.addItem(empty_item)
            return

        for file_path in recent_files:
            item = QListWidgetItem(Path(file_path).name)
            item.setData(Qt.ItemDataRole.UserRole, file_path)
            item.setToolTip(file_path)
            self.recent_files_list.addItem(item)

    def open_recent_file(self, item: QListWidgetItem) -> None:
        """Open a file from the recent files list (single-click or double-click)."""
        file_path = item.data(Qt.ItemDataRole.UserRole)

        if not file_path:
            return

        selected_path = Path(str(file_path))

        if selected_path.exists():
            self._set_selected_file(selected_path)
            return

        self.recent_files_manager.remove_file(selected_path)
        self.refresh_recent_files()
        QMessageBox.warning(
            self,
            "Recent File Missing",
            f"The file no longer exists:\n{selected_path}",
        )

    # ------------------------------------------------------------------
    # Logging and progress
    # ------------------------------------------------------------------

    def log(self, message: str) -> None:
        """Append a message to the log panel."""
        self.log_box.append(message)

    def set_progress(self, value: int) -> None:
        """Set the progress bar value."""
        self.progress_bar.setValue(value)

    def set_status(self, message: str) -> None:
        """Set the current status bar message."""
        self.status_bar.showMessage(message)

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    def validate_input(self) -> bool:
        """Validate that an Excel file has been selected."""
        if not self.file_path:
            QMessageBox.warning(
                self,
                "No File Selected",
                "Please select an Excel file first.",
            )
            return False
        return True

    # ------------------------------------------------------------------
    # Output folder
    # ------------------------------------------------------------------

    def open_output_folder(self) -> None:
        """Open the current output folder with the operating system."""
        output_folder = Path(self.output_folder_edit.text())

        if not output_folder.exists():
            QMessageBox.warning(
                self,
                "Output Folder Not Found",
                f"The output folder does not exist: {output_folder}",
            )
            return

        os.startfile(output_folder)

    # ------------------------------------------------------------------
    # Processing pipeline
    # ------------------------------------------------------------------

    def show_statistics(self, processor: ExcelProcessor) -> None:
        """Log and display processing statistics."""
        self.set_status("Generating Statistics...")
        stats_summary = StatisticsEngine(processor.df).generate_summary()
        processor_summary = processor.get_summary()

        self.statistics_panel.update_statistics(processor_summary, stats_summary)

        self.log("")
        self.log("========== PROCESS SUMMARY ==========")
        self.log(f"Original Rows      : {processor_summary['original_rows']}")
        self.log(f"Current Rows       : {processor_summary['current_rows']}")
        self.log(f"Removed Empty Rows : {processor_summary['removed_empty_rows']}")
        self.log(f"Removed Duplicates : {processor_summary['removed_duplicates']}")
        self.log("-------------------------------------")
        self.log(f"Columns            : {stats_summary['columns']}")
        self.log(f"Numeric Columns    : {stats_summary['numeric_columns']}")
        self.log(f"Text Columns       : {stats_summary['text_columns']}")
        self.log(f"Missing Cells      : {stats_summary['missing_cells']}")
        self.log(f"Memory Usage       : {stats_summary['memory_usage']}")
        self.log("=====================================")

    def load_excel_file(self) -> ExcelProcessor:
        """Load the selected Excel file and return its processor."""
        processor = ExcelProcessor()
        self.set_status("Loading Excel...")
        self.set_progress(10)
        self.log("Loading Excel file...")
        processor.load_excel(self.file_path)
        self.set_progress(25)
        self.log("Excel loaded successfully.")
        return processor

    def clean_excel(self, processor: ExcelProcessor) -> None:
        """Run selected cleanup operations."""
        self.set_status("Cleaning Data...")

        if self.remove_empty_rows_checkbox.isChecked():
            self.log("Removing empty rows...")
            processor.remove_empty_rows()
            self.set_progress(45)
            self.log("Empty rows removed.")

        if self.remove_duplicate_rows_checkbox.isChecked():
            self.log("Removing duplicate rows...")
            processor.remove_duplicates()
            self.set_progress(65)
            self.log("Duplicate rows removed.")

    def save_excel(self, processor: ExcelProcessor) -> None:
        """Save the cleaned Excel file."""
        output_file = Path(self.output_folder_edit.text()) / "cleaned_data.xlsx"
        self.set_status("Saving Files...")
        self.log("Saving Excel file...")
        processor.save_excel(output_file)
        self.set_progress(80)
        self.log(f"Saved to: {output_file}")

    def generate_charts(self, processor: ExcelProcessor) -> None:
        """Generate charts when the chart operation is selected."""
        if not self.generate_charts_checkbox.isChecked():
            return

        output_folder = Path(self.output_folder_edit.text())
        self.set_status("Generating Charts...")
        self.log("Generating charts...")
        self.set_progress(82)

        chart_generator = ChartGenerator(processor.df)
        generated_charts = chart_generator.generate_all(output_folder)
        self.generated_chart_paths = generated_charts

        progress_step = 6 // max(len(generated_charts), 1)
        current_progress = 82

        for chart_path in generated_charts:
            current_progress += progress_step
            self.set_progress(min(current_progress, 88))
            self.log(f"Generated chart: {chart_path}")

    def finish_processing(self, processor: ExcelProcessor) -> None:
        """Finish processing and notify the user."""
        self.set_progress(90)
        self.log("Finalizing processing...")
        processor.reset()
        self.set_progress(95)
        self.log("Processing finalized.")
        self.set_progress(100)
        self.set_status("Completed Successfully")
        self.sucsess_message("Processing completed successfully.")

    def handle_error(self, error_message: str) -> None:
        """Log and display an error message."""
        self.log("")
        self.log("ERROR")
        self.log(error_message)

        QMessageBox.critical(
            self,
            "Error",
            error_message,
        )

    def sucsess_message(self, message: str) -> None:
        """Log and display a success message."""
        self.log("")
        self.log("SUCCESS")
        self.log(message)

        output_folder = Path(self.output_folder_edit.text())
        message_box = QMessageBox(self)
        message_box.setIcon(QMessageBox.Icon.Information)
        message_box.setWindowTitle("Success")
        message_box.setText("Processing Completed Successfully")
        message_box.setInformativeText(self._build_generated_files_text())

        ok_button = message_box.addButton(QMessageBox.StandardButton.Ok)
        open_folder_button = None

        if output_folder.exists():
            open_folder_button = message_box.addButton(
                "Open Output Folder",
                QMessageBox.ButtonRole.ActionRole,
            )

        message_box.exec()

        if message_box.clickedButton() == open_folder_button:
            os.startfile(output_folder)
        elif message_box.clickedButton() == ok_button:
            return

    def _build_generated_files_text(self) -> str:
        """Build the generated files summary for the success dialog."""
        generated_files = ["Generated Files", "", "- cleaned_data.xlsx"]

        if self.generated_chart_paths:
            generated_files.append("- generated charts")

        return "\n".join(generated_files)

    def process_excel(self) -> None:
        """Process the selected Excel file."""
        if not self.validate_input():
            return

        self.progress_bar.setValue(0)
        self.generated_chart_paths = []
        self.log("Starting Excel processing...")

        try:
            processor = self.load_excel_file()
            self.clean_excel(processor)
            self.save_excel(processor)
            self.generate_charts(processor)
            self.show_statistics(processor)
            self.finish_processing(processor)
        except Exception as error:
            self.handle_error(str(error))
