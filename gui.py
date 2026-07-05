from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QLabel,
    QPushButton,
    QFileDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
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

        layout = QVBoxLayout()

        title = QLabel("Excel Automation Toolkit")
        layout.addWidget(title)

        row = QHBoxLayout()

        self.path_edit = QLineEdit()
        self.path_edit.setReadOnly(True)

        browse_button = QPushButton("Browse Excel")
        browse_button.clicked.connect(self.browse_excel)

        row.addWidget(self.path_edit)
        row.addWidget(browse_button)

        layout.addLayout(row)

        self.process_button = QPushButton("Process")
        layout.addWidget(self.process_button)

        central.setLayout(layout)

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