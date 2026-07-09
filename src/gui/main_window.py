import os
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QFileDialog,
    QCheckBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QStatusBar,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from src.core.charts import ChartGenerator
from src.core.excel_processor import ExcelProcessor
from src.core.statistics import StatisticsEngine
from src.gui.statistics_panel import StatisticsPanel
from services.recent_files_manager import RecentFilesManager


class MainWindow(QMainWindow):
    """Main window for the Excel Automation Toolkit."""

    def __init__(self) -> None:
        """Initialize the main application window."""
        super().__init__()

        self.setWindowTitle("Excel Automation Toolkit")
        self.resize(800, 500)

        self.file_path = ""
        self.generated_chart_paths: list[Path] = []
        self.recent_files_manager = RecentFilesManager()

        self.setup_ui()
        self._build_status_bar()
        self._build_menu_bar()
        self.refresh_recent_files()

    def setup_ui(self) -> None:
        """Build the main application interface."""
        central = QWidget()
        self.setCentralWidget(central)

        main_layout = QVBoxLayout()

        title = QLabel("Excel Automation Toolkit")
        main_layout.addWidget(title)
        main_layout.addLayout(self._build_file_selection_layout())
        main_layout.addWidget(self._build_recent_files_group())
        main_layout.addWidget(self._build_operations_group())
        main_layout.addWidget(QLabel("Output Folder"))

        self.output_folder_edit = QLineEdit("output/")
        self.output_folder_edit.setReadOnly(True)
        self.output_folder_edit.setToolTip("Folder where generated files are saved.")
        main_layout.addWidget(self.output_folder_edit)

        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setToolTip("Processing progress.")
        main_layout.addWidget(self.progress_bar)

        main_layout.addLayout(self._build_results_layout())

        main_layout.addLayout(self._build_action_buttons_layout())

        central.setLayout(main_layout)

    def _build_file_selection_layout(self) -> QHBoxLayout:
        """Create the file selection controls."""
        file_selection_layout = QHBoxLayout()

        self.path_edit = QLineEdit()
        self.path_edit.setReadOnly(True)
        self.path_edit.setToolTip("Selected Excel file path.")

        browse_button = QPushButton("Browse Excel")
        browse_button.setToolTip("Choose an Excel file to process.")
        browse_button.clicked.connect(self.browse_excel)

        file_selection_layout.addWidget(self.path_edit)
        file_selection_layout.addWidget(browse_button)

        return file_selection_layout

    def _build_recent_files_group(self) -> QGroupBox:
        """Create the recent files list container."""
        recent_files_group = QGroupBox("Recent Files")
        recent_files_group.setToolTip("Quickly reopen recently used Excel files.")

        layout = QVBoxLayout()

        self.recent_files_list = QListWidget()
        self.recent_files_list.setToolTip("Recently opened Excel files.")
        self.recent_files_list.itemClicked.connect(self.open_recent_file)

        layout.addWidget(self.recent_files_list)
        recent_files_group.setLayout(layout)
        return recent_files_group

    def _build_operations_group(self) -> QGroupBox:
        """Create the operations checkbox group."""
        operations_group = QGroupBox("Operations")
        operations_group.setToolTip("Select which operations to run.")
        operations_layout = QVBoxLayout()

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

        self.generate_statistics_checkbox = QCheckBox("Generate Statistics")
        self.generate_statistics_checkbox.setToolTip(
            "Generate summary statistics for the processed data."
        )
        self.generate_charts_checkbox = QCheckBox("Generate Charts")
        self.generate_charts_checkbox.setToolTip(
            "Generate chart images in the output charts folder."
        )
        self.generate_pdf_report_checkbox = QCheckBox("Generate PDF Report")
        self.generate_pdf_report_checkbox.setToolTip(
            "Reserve report generation for PDF output."
        )

        operations_layout.addWidget(self.remove_empty_rows_checkbox)
        operations_layout.addWidget(self.remove_duplicate_rows_checkbox)
        operations_layout.addWidget(self.generate_statistics_checkbox)
        operations_layout.addWidget(self.generate_charts_checkbox)
        operations_layout.addWidget(self.generate_pdf_report_checkbox)

        operations_group.setLayout(operations_layout)
        return operations_group

    def _build_results_layout(self) -> QHBoxLayout:
        """Create the side-by-side log and statistics panels."""
        results_layout = QHBoxLayout()

        log_group = QGroupBox("Log")
        log_layout = QVBoxLayout()

        self.log_box = QTextEdit()
        self.log_box.setReadOnly(True)
        self.log_box.setText("Application started.")
        self.log_box.setToolTip("Processing messages and results.")

        log_layout.addWidget(self.log_box)
        log_group.setLayout(log_layout)

        self.statistics_panel = StatisticsPanel()
        self.statistics_panel.setToolTip("Statistics for the processed workbook.")

        results_layout.addWidget(log_group, 2)
        results_layout.addWidget(self.statistics_panel, 1)

        return results_layout

    def _build_action_buttons_layout(self) -> QHBoxLayout:
        """Create the main action buttons."""
        action_buttons_layout = QHBoxLayout()

        self.process_button = QPushButton("Process")
        self.process_button.setToolTip("Run the selected Excel operations.")
        self.process_button.clicked.connect(self.process_excel)

        self.open_output_folder_button = QPushButton("📂 Open Output Folder")
        self.open_output_folder_button.setToolTip(
            "Open the configured output folder."
        )
        self.open_output_folder_button.clicked.connect(self.open_output_folder)

        action_buttons_layout.addWidget(self.process_button)
        action_buttons_layout.addWidget(self.open_output_folder_button)

        return action_buttons_layout

    def _build_status_bar(self) -> None:
        """Create the main window status bar."""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.set_status("Ready")

    def _build_menu_bar(self) -> None:
        """Create the application menu bar."""
        help_menu = self.menuBar().addMenu("Help")

        about_action = QAction("About", self)
        about_action.setStatusTip("About Excel Automation Toolkit")
        about_action.triggered.connect(self.show_about_dialog)

        help_menu.addAction(about_action)

    def show_about_dialog(self) -> None:
        """Display application information."""
        QMessageBox.about(
            self,
            "About Excel Automation Toolkit",
            (
                "<b>Excel Automation Toolkit</b><br>"
                "Version 1.1.0<br><br>"
                "Developer: Halit Tiryaki<br><br>"
                "<b>Technologies</b><br>"
                "Python<br>"
                "PySide6<br>"
                "Pandas<br>"
                "OpenPyXL<br>"
                "Matplotlib"
            ),
        )

    def browse_excel(self) -> None:
        """Open a file dialog and store the selected Excel file path."""
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "Select Excel File",
            "",
            "Excel Files (*.xlsx *.xls)",
        )

        if file_name:
            self._set_selected_file(file_name)

    def _set_selected_file(self, file_path: str | Path) -> None:
        """Set the active file path and persist it in recent files."""
        normalized_path = Path(file_path).expanduser().resolve(strict=False)
        self.file_path = str(normalized_path)
        self.path_edit.setText(self.file_path)
        self.recent_files_manager.add_file(self.file_path)
        self.refresh_recent_files()

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
            self.recent_files_list.addItem(item)

    def open_recent_file(self, item: QListWidgetItem) -> None:
        """Open a file from the recent files list."""
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

    def log(self, message: str) -> None:
        """Append a message to the log panel."""
        self.log_box.append(message)

    def set_progress(self, value: int) -> None:
        """Set the progress bar value."""
        self.progress_bar.setValue(value)

    def set_status(self, message: str) -> None:
        """Set the current status bar message."""
        self.status_bar.showMessage(message)

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
