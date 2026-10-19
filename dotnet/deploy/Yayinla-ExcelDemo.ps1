$ErrorActionPreference = "Stop"
# EXCEL DEMO YAYIN BETIGI -> demo-excel.halittiryaki.com
# Calistir: powershell -ExecutionPolicy Bypass -File "$HOME\Desktop\halittiryakicom\Portfolio\Excel Automation Toolkit\dotnet\deploy\Yayinla-ExcelDemo.ps1"
# Ilk kurulum adimlari: PLESK-KURULUM.md

$kok = "$HOME\Desktop\halittiryakicom\Portfolio\Excel Automation Toolkit"
cd $kok
$dal = git branch --show-current
if ($dal -ne "feat/dotnet-v2") { throw "Dal feat/dotnet-v2 degil: $dal" }

$deploy = "$kok\dotnet\deploy"
$pub = "$deploy\out\publish"
New-Item -ItemType Directory -Force "$deploy\out\zip" | Out-Null
$zip = "$deploy\out\zip\excel-demo-$(Get-Date -Format 'yyyy-MM-dd-HHmm').zip"

# Testler gecmeden yayin yok
dotnet test "$kok\dotnet\ExcelToolkit.slnx" -c Release
if ($LASTEXITCODE -ne 0) { throw "Testler gecmedi, yayin yapilmadi" }

# Eski yayini temizle (kalan eski dosyalar zip'e girmesin)
if (Test-Path $pub) { Remove-Item $pub -Recurse -Force }

dotnet publish "$kok\dotnet\src\ExcelToolkit.Web\ExcelToolkit.Web.csproj" -c Release -o $pub
if ($LASTEXITCODE -ne 0) { throw "Publish hata verdi, zip yapilmadi" }

# Kontrol: .pdb listesi bos donmeli; web.config'de "webSocket" gecmeli
Get-ChildItem $pub -Filter "*.pdb"
Select-String -Path "$pub\web.config" -Pattern "webSocket|AspNetCoreModuleV2" | Select-Object -ExpandProperty Line

Compress-Archive -Path "$pub\*" -DestinationPath $zip -Force
Get-Item $zip | Select-Object Name, @{n='MB';e={[math]::Round($_.Length/1MB,1)}}

# YUKLEME: Plesk > demo-excel.halittiryaki.com > Dosyalar > httpdocs
# (1) app_offline.htm yukle (bu klasorde)  (2) zip yukle > Extract (uzerine yaz) > zip'i sil
# (3) SON ADIM: app_offline.htm'i SIL
# (4) Claude'a "yayinda" yaz -> canli kontrol
