using System.Globalization;
using System.Threading.RateLimiting;
using ExcelToolkit.Web.Components;
using Microsoft.AspNetCore.DataProtection;
using Microsoft.AspNetCore.HttpOverrides;

// Sayı ve tarih biçimi Türkçe (1.234,56 · 16.10.2026)
var turkish = CultureInfo.GetCultureInfo("tr-TR");
CultureInfo.DefaultThreadCurrentCulture = turkish;
CultureInfo.DefaultThreadCurrentUICulture = turkish;

var builder = WebApplication.CreateBuilder(args);

builder.Services.AddRazorComponents()
    .AddInteractiveServerComponents();

// Plesk/IIS arkasında gerçek ziyaretçi IP'si ve https bilgisi (IP başına sınır doğru çalışsın)
builder.Services.Configure<ForwardedHeadersOptions>(options =>
{
    options.ForwardedHeaders = ForwardedHeaders.XForwardedFor | ForwardedHeaders.XForwardedProto;
    options.KnownIPNetworks.Clear();
    options.KnownProxies.Clear();
});

// Anahtarlar App_Data'da kalır: uygulama havuzu yeniden başlayınca açık sayfalar bozulmaz.
// App_Data web'den sunulmaz (yalnız wwwroot sunulur) ve git'e girmez.
builder.Services.AddDataProtection()
    .SetApplicationName("ExcelToolkit.Web")
    .PersistKeysToFileSystem(new DirectoryInfo(
        Path.Combine(builder.Environment.ContentRootPath, "App_Data", "DataProtection-Keys")));

// IP başına dakikada sınırlı sayfa isteği (demo kötüye kullanılmasın)
builder.Services.AddRateLimiter(options =>
{
    options.RejectionStatusCode = StatusCodes.Status429TooManyRequests;
    options.AddPolicy("ip", context => RateLimitPartition.GetFixedWindowLimiter(
        context.Connection.RemoteIpAddress?.ToString() ?? "bilinmiyor",
        _ => new FixedWindowRateLimiterOptions
        {
            PermitLimit = 30,
            Window = TimeSpan.FromMinutes(1),
            QueueLimit = 0,
        }));
});

var app = builder.Build();

app.UseForwardedHeaders();

// Güvenlik başlıkları: başka sitelerin çerçevesine gömülmesin, tür tahmini kapalı
app.Use(async (context, next) =>
{
    var headers = context.Response.Headers;
    headers["X-Content-Type-Options"] = "nosniff";
    headers["X-Frame-Options"] = "DENY";
    headers["Referrer-Policy"] = "strict-origin-when-cross-origin";
    headers["Content-Security-Policy"] = "frame-ancestors 'none'; base-uri 'self'; object-src 'none'";
    await next();
});

if (!app.Environment.IsDevelopment())
{
    app.UseExceptionHandler("/Error", createScopeForErrors: true);
    app.UseHsts();
}

app.UseHttpsRedirection();
app.UseRateLimiter();
app.UseAntiforgery();

// Canlı kontrol için: yalnız "ok" döner, bilgi sızdırmaz
app.MapGet("/healthz", () => Results.Text("ok"));

app.MapStaticAssets();
app.MapRazorComponents<App>()
    .AddInteractiveServerRenderMode()
    .RequireRateLimiting("ip");

app.Run();
