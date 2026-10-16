# Excel Automation Toolkit v2 (.NET 10)

v1 (Python / PySide6) depo kökünde, `v1.2.1` etiketiyle donduruldu. v2 bu klasörde geliştiriliyor (dal `feat/dotnet-v2`).
Plan: `halittiryakicom/Protocols/Planlar/HT-Excel-v2-NET-Plani.md`

## Gerekenler
- .NET 10 SDK (`dotnet --version` → 10.0.x)

## Çalıştırma
```powershell
cd dotnet
dotnet test                                  # testler
dotnet run --project src/ExcelToolkit.Web    # web demo → https://localhost:7180
```

## Yapı
```
dotnet/
├─ ExcelToolkit.slnx
├─ src/ExcelToolkit.Core          okuma (.xlsx, .csv) · temizleme · istatistik · kaydetme (.xlsx) · tek adımda işleme
├─ src/ExcelToolkit.Web           Blazor Web App demo: yükle → temizle → özet → indir
└─ tests/ExcelToolkit.Core.Tests  xUnit · v1 ile aynı sonuç testi (TestData/sample_employee_data.xlsx)
```

## M1 durumu
- [x] Çözüm iskeleti, ortak ayarlar (`Directory.Build.props`, `global.json`)
- [x] Okuma: `.xlsx` (ClosedXML, formüller çalıştırılmaz) · `.csv` (ayırıcı ve kodlama otomatik, Türkçe sayı/tarih) · `.xlsm` ve `.xls` reddedilir · satır sınırı
- [x] Temizleme: boş satır + tekrar satır (v1 ile aynı sıra ve sonuç)
- [x] İstatistik: satır/sütun, sayısal/metin sütun, boş hücre, sütun türü; sayısal sütunlarda toplam/ortalama/min/maks/medyan/std (v1 ile aynı değerler)
- [x] Kaydetme (.xlsx): kalın ve sabit başlık, filtre, sütun genişliği; "=" ile başlayan metin formül olmaz
- [ ] `.xls` desteği (ExcelDataReader)

## M2 durumu (web demo, hedef 30.10)
- [x] Blazor Web App iskeleti (etkileşimli sunucu modu), Türkçe arayüz
- [x] Yükleme: .xlsx / .csv · en fazla 10 MB · 50.000 satır · dosya diske yazılmaz, bellekte işlenir, 30 dk sonra silinir
- [x] Seçenekler: boş satır / tekrar satır · tekrar işle
- [x] Özet kartları + sütun özeti tablosu + ilk 20 satır önizleme
- [x] Temiz dosyayı .xlsx indir (sunucuda dosya tutulmaz)
- [x] IP başına dakikada 30 istek sınırı
- [ ] Plesk: demo-excel.halittiryaki.com alt alan adı + SSL + yayın
- [ ] Gizlilik/aydınlatma notu, halittiryaki.com'a bağlantı
