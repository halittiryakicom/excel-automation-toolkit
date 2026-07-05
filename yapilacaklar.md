Teknoloji
Python 3.12+
CustomTkinter (Modern arayüz)
pandas
openpyxl
matplotlib
reportlab
Pillow


Proje Yapısı
excel-automation-toolkit/
│
├── app.py
├── requirements.txt
├── README.md
├── LICENSE
│
├── assets/
│   ├── logo.png
│   └── icon.ico
│
├── data/
│   └── sample.xlsx
│
├── output/
│   ├── report.pdf
│   ├── report.xlsx
│   └── charts/
│
├── src/
│   ├── gui.py
│   ├── excel_processor.py
│   ├── report_generator.py
│   ├── charts.py
│   ├── utils.py
│   └── settings.py
│
└── screenshots/


Arayüz

Tek pencereli modern bir uygulama.
--------------------------------------------
 Excel Automation Toolkit
--------------------------------------------
📂 Select Excel File
[ ................. ] [Browse]
--------------------------------------------
☑ Remove Empty Rows
☑ Remove Duplicate Rows
☑ Calculate Statistics
☑ Generate Charts
☑ Export New Excel
☑ Generate PDF Report
--------------------------------------------
Output Folder
[....................]
--------------------------------------------

             [ PROCESS ]
--------------------------------------------
Progress Bar
--------------------------------------------
Log
Loaded file...
Processing...
Creating charts...
Done.


Özellikler
Excel okuma
xlsx
xlsm


Temizleme
✅ Boş satır silme
✅ Tekrar eden satır silme

Analiz
Ortalama
Toplam
Min
Max
Medyan
Standart sapma


Grafik
Bar Chart
Pie Chart
Line Chart
PNG olarak kaydedilecek.


Excel çıktısı
Yeni bir Excel oluşturacak.

İçinde:
temiz veri
özet
grafikler


PDF raporu

Kapak
↓
İstatistikler
↓
Grafikler
↓
Oluşturulma tarihi
↓
Sayfa numarası

README
GitHub'da şunlar olacak.
Screenshots
Features
Installation
Usage
Requirements
Example Outputs