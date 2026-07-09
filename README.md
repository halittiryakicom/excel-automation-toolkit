![Python](https://img.shields.io/badge/Python-3.11-blue)
![PySide6](https://img.shields.io/badge/PySide6-GUI-green)
![Pandas](https://img.shields.io/badge/Pandas-Data%20Processing-blue)
![Matplotlib](https://img.shields.io/badge/Matplotlib-Charts-orange)
![License](https://img.shields.io/badge/License-MIT-yellow)
![Release](https://img.shields.io/github/v/release/halittiryakicom/excel-automation-toolkit)
![Platform](https://img.shields.io/badge/Platform-Windows-blueviolet)

# 📊 Excel Automation Toolkit

A modern desktop application built with **Python** and **PySide6** for cleaning, processing, analyzing and visualizing Excel files.

The application provides automatic Excel cleaning, statistical analysis, chart generation and an intuitive desktop interface.

This project was developed as part of my software engineering portfolio to demonstrate clean architecture, desktop application development and data automation using Python.

---

# ✨ Features

## 📂 Excel Processing

- Load Excel (.xlsx / .xls) files
- Remove empty rows
- Remove duplicate rows
- Save cleaned Excel files automatically

---

## ✅ Recent Files Support

- Quickly reopen previously used Excel files.
- Stores up to 5 recent files.
- Automatically removes missing files.
- Improves workflow.

---

## 📈 Statistics Dashboard

Generate useful information about your dataset.

- Original rows
- Current rows
- Removed empty rows
- Removed duplicate rows
- Total columns
- Numeric columns
- Text columns
- Missing cells
- Memory usage

---

## 📊 Automatic Chart Generation

Generate charts automatically after processing.

Current charts include:

- Missing Values Chart
- Column Types Chart
- Numeric Distribution Chart

Charts are exported as PNG files.

---

## 🖥 Modern Desktop Interface

- PySide6 GUI
- Statistics Panel
- Processing Log
- Progress Bar
- Status Bar
- About Dialog
- Tooltips
- Open Output Folder
- Success Dialog

---

# 🛠 Technologies

- Python 3.11+
- PySide6
- Pandas
- OpenPyXL
- Matplotlib

---

# 📁 Project Structure

```text
excel-automation-toolkit/

├── app.py
├── requirements.txt
├── LICENSE
├── README.md
│
├── output/
│   ├── cleaned_data.xlsx
│   └── charts/
│
├── config/
│   └── recent_files.json
│
├── services/
│   └── recent_files_manager.py
│
└── src/
    ├── core/
    │   ├── excel_processor.py
    │   ├── statistics.py
    │   └── charts.py
    │
    └── gui/
        ├── main_window.py
        └── statistics_panel.py
```

---

# 🚀 Installation

Clone the repository

```bash
git clone https://github.com/halittiryakicom/excel-automation-toolkit.git
```

Enter the project folder

```bash
cd excel-automation-toolkit
```

Install dependencies

```bash
pip install -r requirements.txt
```

Run the application

```bash
python app.py
```

---

# 📷 Screenshots

## Main Window

![Main Window](screenshots/mainwindow.png)

---

## Processing Result

![Processing Result](screenshots/result.png)

---

## Generated Charts

![alt text](screenshots/column_types.png)
![alt text](screenshots/missing_values.png)
![alt text](screenshots/numeric_distribution.png)

---

# 🔄 Workflow

```text
Select Excel File
        │
        ▼
Load Excel
        │
        ▼
Clean Data
        │
        ▼
Generate Statistics
        │
        ▼
Generate Charts
        │
        ▼
Save Results
```

---

# 📦 Output

After processing, the application automatically creates:

```text
output/

├── cleaned_data.xlsx

└── charts/

    ├── missing_values.png

    ├── column_types.png

    └── numeric_distribution.png
```

---

# 🎯 Project Goals

This project demonstrates:

- Desktop Application Development
- Data Cleaning Automation
- Excel Processing
- Object-Oriented Programming
- Modular Architecture
- Data Visualization
- Python GUI Development

---

# 🗺 Roadmap

## ✅ Version 1.1.0

- Excel Processing
- Statistics Dashboard
- Chart Generation
- Processing Log
- Progress Bar
- Status Bar
- About Dialog
- Tooltips
- Open Output Folder
- GitHub Release
- Recent Files Support

---

## 🚀 Version 1.2 (Planned)

- PDF Report Generator
- Batch Processing
- CSV Support
- Drag & Drop
- Multi-sheet Processing
- Export Statistics
- Dark Theme
- Settings Panel

---

# 📄 License

Licensed under the MIT License.

---

# 👨‍💻 Author

**Halit Tiryaki**

Computer Teacher • Python Developer • Desktop Application Developer

GitHub

https://github.com/halittiryakicom

---

⭐ If you like this project, consider giving it a star.