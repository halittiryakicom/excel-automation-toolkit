# Excel Automation Toolkit v2 (.NET 10)

v1 (Python / PySide6) depo kökünde, `v1.2.1` etiketiyle donduruldu. v2 bu klasörde geliştiriliyor (dal `feat/dotnet-v2`).
Plan: `halittiryakicom/Protocols/Planlar/HT-Excel-v2-NET-Plani.md`

## Gerekenler
- .NET 10 SDK (`dotnet --version` → 10.0.x)

## Çalıştırma
```powershell
cd dotnet
dotnet test
```

## Yapı
```
dotnet/
├─ ExcelToolkit.slnx
├─ src/ExcelToolkit.Core          okuma (.xlsx, .csv) · temizleme (boş/tekrar satır)
└─ tests/ExcelToolkit.Core.Tests  xUnit · v1 ile aynı sonuç testi (TestData/sample_employee_data.xlsx)
```

## M1 durumu
- [x] Çözüm iskeleti, ortak ayarlar (`Directory.Build.props`, `global.json`)
- [x] Okuma: `.xlsx` (ClosedXML, formüller çalıştırılmaz) · `.csv` (ayırıcı ve kodlama otomatik, Türkçe sayı/tarih) · `.xlsm` ve `.xls` reddedilir · satır sınırı
- [x] Temizleme: boş satır + tekrar satır (v1 ile aynı sıra ve sonuç)
- [ ] İstatistik (satır/sütun, sayısal/metin sütun, boş hücre, ortalama/toplam/min/maks/medyan/std)
- [ ] Kaydetme (.xlsx)
- [ ] `.xls` desteği (ExcelDataReader)
