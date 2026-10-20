# demo-excel.halittiryaki.com — Plesk ilk kurulum (bir kez)

Uygulama: `dotnet/src/ExcelToolkit.Web` (Blazor Web App, .NET 10). Veritabanı yok, dosya diske yazılmaz.
Sunucuda .NET / ASP.NET Core Runtime **10.0.12** kurulu (16.10 destek cevabı) → ek kurulum gerekmez.
Şifre, anahtar, bağlantı dizesi **yok**: bu uygulamanın gizli bir ayarı bulunmuyor.

## 1. Alt alan adı (≈5 dk)
1. Plesk → **Websiteler ve Alan Adları** → halittiryaki.com → **Alt Alan Adı Ekle**
2. Ad: `demo-excel` · Belge kökü: Plesk'in önerdiği klasör (ör. `demo-excel.halittiryaki.com`) — **adını not et**, yükleme oraya yapılacak
3. **DNS kontrolü:** halittiryaki.com'un DNS'i Plesk'teyse kayıt kendiliğinden açılır. DNS başka yerdeyse (alan adı firması) oraya `demo-excel` için **A kaydı** → sunucu IP'si (halittiryaki.com ile aynı IP) ekle. Yayılma birkaç dakika–birkaç saat.

## 2. SSL (≈3 dk)
1. Alt alan adı → **SSL/TLS Sertifikaları** → **Let's Encrypt** → `demo-excel.halittiryaki.com` işaretli → Al
2. **Barındırma Ayarları** → "HTTP'den HTTPS'ye kalıcı 301 yönlendirme" **açık**

## 3. ASP.NET Core ayarı
- halittiryaki.com'da nasıl ayarlıysa aynısı: barındırma türü web sitesi, **ASP.NET Core / .NET Core** desteği açık.
- Mümkünse **ayrı (dedicated) uygulama havuzu**: demo yoğunlaşırsa ana siteyi etkilemez.
- **WebSocket:** IIS'te açıksa Blazor hızlı bağlantı kullanır; kapalıysa kendiliğinden yavaş yönteme düşer, site yine çalışır. Yayından sonra Claude kontrol eder.

## 4. İlk yayın
```powershell
powershell -ExecutionPolicy Bypass -File "$HOME\Desktop\halittiryakicom\Portfolio\Excel Automation Toolkit\dotnet\deploy\Yayinla-ExcelDemo.ps1"
```
Betik: dal kontrolü → testler → publish → zip (`dotnet\deploy\out\zip\`).
Yükleme: Plesk → alt alan adı → **Dosyalar** → belge kökü →
(1) `app_offline.htm` yükle → (2) zip'i yükle → **Çıkart (üzerine yaz)** → zip'i sil → (3) **app_offline.htm'i sil**

## 5. İlk yayından sonra
- `App_Data\DataProtection-Keys` klasörü ilk açılışta kendiliğinden oluşur. Oluşmadıysa: Dosya Yöneticisi → `App_Data` klasörü oluştur → izinler → uygulama havuzu kullanıcısına **yazma** ver.
- Claude'a "excel demo yayında" yaz → canlı kontrol: `/healthz` = ok, örnek dosya yükle-temizle-indir, telefon görünümü, güvenlik başlıkları, WebSocket.

## Sorun çıkarsa
| Belirti | Neden / çözüm | 
|---|---|
| 500.30 / 502.5 | Runtime ya da uygulama başlamıyor → `web.config`'de `stdoutLogEnabled="true"` yap, `logs\` klasörünü oluştur, tekrar aç, logu Claude'a gönder (sonra kapat) |
| Let's Encrypt: "Timeout after connect" / 404 (HTTP doğrulama) veya "NXDOMAIN _acme-challenge" (DNS doğrulama) (20.10'da yaşandı) | HTTP: IIS her isteği uygulamaya veriyor → uygulama artık `/.well-known/` klasörünü kendisi sunuyor (Program.cs, HTTPS yönlendirmesinden önce) → yeniden yayın → Let's Encrypt **HTTP (http-01)** ile tekrar. DNS: alt alan adının TXT kaydı yetkili DNS'e düşmüyor → HTTP yöntemini kullan. Not: Let's Encrypt saatte en fazla 5 başarısız denemeye izin verir |
| 500.34 "does not support mixing hosting models" (19.10'da yaşandı) | Alt alan adı ana sitenin uygulama havuzunu paylaşıyor; ana site out-of-process. Çözüm: projede `AspNetCoreHostingModel=OutOfProcess` (yapıldı) → yeniden yayın. Alternatif: Plesk'te alt alan adına ayrı uygulama havuzu |
| 400 "Bad Request – Invalid Hostname" | Adres `AllowedHosts` listesinde değil (`appsettings.Production.json`) |
| Sayfa açılıyor ama düğmeler çalışmıyor | Blazor bağlantısı kurulamıyor → tarayıcı konsolu / WebSocket ayarı |
| Sertifika uyarısı | Let's Encrypt alınmadan önce DNS yayılmamış → DNS'i bekle, sertifikayı yeniden al |
| `ERR_CERT_COMMON_NAME_INVALID` (19.10'da yaşandı) | Alt alan adına başka adın sertifikası (ana alan adı / Plesk varsayılanı) sunuluyor → alt alan adı → SSL/TLS Sertifikaları → Let's Encrypt (`demo-excel.halittiryaki.com`) → **Barındırma Ayarları → Sertifika** listesinde bunu seç. halittiryaki.com HSTS `includeSubDomains; preload` gönderdiği için tarayıcı "yine de devam et" seçeneği **vermez**; geçerli sertifika şart. |
