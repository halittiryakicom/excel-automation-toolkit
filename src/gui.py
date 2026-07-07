from core.excel_processor import ExcelProcessor
from core.statistics import StatisticsEngine
from pathlib import Path
from PySide6.QtWidgets import (
    QMainWindow,
    QMessageBox,
    QWidget,
    QLabel,
    QPushButton,
    QFileDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QGroupBox,
    QCheckBox,
    QProgressBar,
    QTextEdit,
)

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Excel Automation Toolkit")
        self.resize(800, 500)

        self.file_path = ""

        self.setup_ui()

    def setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)

        main_layout = QVBoxLayout()

        title = QLabel("Excel Automation Toolkit")
        main_layout.addWidget(title)

        file_selection_layout = QHBoxLayout()

        self.path_edit = QLineEdit()
        self.path_edit.setReadOnly(True)

        browse_button = QPushButton("Browse Excel")
        browse_button.clicked.connect(self.browse_excel)

        file_selection_layout.addWidget(self.path_edit)
        file_selection_layout.addWidget(browse_button)

        main_layout.addLayout(file_selection_layout)

        operations_group = QGroupBox("Operations")
        operations_layout = QVBoxLayout()

        self.remove_empty_rows_checkbox = QCheckBox("Remove Empty Rows")
        self.remove_empty_rows_checkbox.setChecked(True)

        self.remove_duplicate_rows_checkbox = QCheckBox("Remove Duplicate Rows")
        self.remove_duplicate_rows_checkbox.setChecked(True)

        self.generate_statistics_checkbox = QCheckBox("Generate Statistics")
        self.generate_charts_checkbox = QCheckBox("Generate Charts")
        self.generate_pdf_report_checkbox = QCheckBox("Generate PDF Report")

        operations_layout.addWidget(self.remove_empty_rows_checkbox)
        operations_layout.addWidget(self.remove_duplicate_rows_checkbox)
        operations_layout.addWidget(self.generate_statistics_checkbox)
        operations_layout.addWidget(self.generate_charts_checkbox)
        operations_layout.addWidget(self.generate_pdf_report_checkbox)

        operations_group.setLayout(operations_layout)
        main_layout.addWidget(operations_group)

        output_folder_label = QLabel("Output Folder")
        main_layout.addWidget(output_folder_label)

        self.output_folder_edit = QLineEdit("output/")
        self.output_folder_edit.setReadOnly(True)
        main_layout.addWidget(self.output_folder_edit)

        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        main_layout.addWidget(self.progress_bar)

        self.log_box = QTextEdit()
        self.log_box.setReadOnly(True)
        self.log_box.setText("Application started.")
        main_layout.addWidget(self.create_statistics_panel())

        self.process_button = QPushButton("Process")
        self.process_button.clicked.connect(self.process_excel)
        main_layout.addWidget(self.process_button)
        

        central.setLayout(main_layout)

    def create_statistics_panel(self):
        self.statistics_group = QGroupBox("Statistics")

        layout = QVBoxLayout()
        self.original_rows_label = QLabel("Original Rows : -")
        self.current_rows_label = QLabel("Current Rows : -")
        self.empty_rows_label = QLabel("Removed Empty : -")
        self.duplicate_rows_label = QLabel("Removed Duplicate : -")
        self.columns_label = QLabel("Columns : -")
        self.numeric_columns_label = QLabel("Numeric Columns : -")
        self.text_columns_label = QLabel("Text Columns : -")
        self.missing_cells_label = QLabel("Missing Cells : -")
        self.memory_usage_label = QLabel("Memory Usage : -")

        layout.addWidget(self.original_rows_label)
        layout.addWidget(self.current_rows_label)
        layout.addWidget(self.empty_rows_label)
        layout.addWidget(self.duplicate_rows_label)
        layout.addWidget(self.columns_label)
        layout.addWidget(self.numeric_columns_label)
        layout.addWidget(self.text_columns_label)
        layout.addWidget(self.missing_cells_label)
        layout.addWidget(self.memory_usage_label)

        layout.addStretch()

        self.statistics_group.setLayout(layout)

    def browse_excel(self):

        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "Select Excel File",
            "",
            "Excel Files (*.xlsx *.xls)"
        )

        if file_name:
            self.file_path = file_name
            self.path_edit.setText(file_name)

    def update_statistics_panel(
        self,
        processor_summary,
        stats_summary
    ):setText()

    def log(self, message):
        self.log_box.append(message)

    def set_progress(self, value):
        self.progress_bar.setValue(value)

    def validate_input(self):
        if not self.file_path:
            QMessageBox.warning(
                self,
                "No File Selected",
                "Please select an Excel file first."
            )
            return False
        return True
    
    def show_statistics(self, processor: ExcelProcessor):
        stats_summary = StatisticsEngine(processor.df).generate_summary()
        processor_summary = processor.get_summary()
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
        processor = ExcelProcessor()
        self.set_progress(10)
        self.log("Loading Excel file...")
        processor.load_excel(self.file_path)
        self.set_progress(25)
        self.log("Excel loaded successfully.")
        return processor

    def clean_excel(
        self,
        processor: ExcelProcessor
    ) -> None:
        # Remove Empty Rows
        if self.remove_empty_rows_checkbox.isChecked():
            self.log("Removing empty rows...")
            processor.remove_empty_rows()
            self.set_progress(45)
            self.log("Empty rows removed.")

        # Remove Duplicate Rows
        if self.remove_duplicate_rows_checkbox.isChecked():
            self.log("Removing duplicate rows...")
            processor.remove_duplicates()
            self.set_progress(65)
            self.log("Duplicate rows removed.")

    def save_excel(self, processor: ExcelProcessor):
        output_file = Path(self.output_folder_edit.text()) / "cleaned_data.xlsx"
        self.log("Saving Excel file...")
        processor.save_excel(output_file)
        self.set_progress(80)
        self.log(f"Saved to: {output_file}")

    def finish_processing(self, processor: ExcelProcessor):
        self.set_progress(90)
        self.log("Finalizing processing...")
        processor.reset()
        self.set_progress(95)
        self.log("Processing finalized.")
        self.set_progress(100)
        self.sucsess_message("Processing completed successfully.")

    def handle_error(self, error_message):
        self.log("")
        self.log("ERROR")
        self.log(error_message)

        QMessageBox.critical(
            self,
            "Error",
            error_message
        )

    def sucsess_message(self, message):
        self.log("")
        self.log("SUCCESS")
        self.log(message)

        QMessageBox.information(
            self,
            "Success",
            message
        )

    def process_excel(self):
        if not self.validate_input():
            return

        self.progress_bar.setValue(0)
        self.log("Starting Excel processing...")

        try:
            processor = self.load_excel_file()
            self.clean_excel(processor)
            self.save_excel(processor)
            self.show_statistics(processor)
            self.finish_processing(processor)

        except Exception as e:
            self.handle_error(str(e))