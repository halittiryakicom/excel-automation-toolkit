from PySide6.QtWidgets import (
    QMainWindow,
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
        main_layout.addWidget(self.log_box)

        self.process_button = QPushButton("Process")
        main_layout.addWidget(self.process_button)

        central.setLayout(main_layout)

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

    def log(self, message):
        self.log_box.append(message)

    def set_progress(self, value):
        self.progress_bar.setValue(value)
