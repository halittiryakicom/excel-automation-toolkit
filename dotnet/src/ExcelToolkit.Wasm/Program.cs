using System.Globalization;
using ExcelToolkit.Wasm;
using Microsoft.AspNetCore.Components.Web;
using Microsoft.AspNetCore.Components.WebAssembly.Hosting;

// Sayı ve tarih biçimi Türkçe (1.234,56 · 16.10.2026)
var turkish = CultureInfo.GetCultureInfo("tr-TR");
CultureInfo.DefaultThreadCurrentCulture = turkish;
CultureInfo.DefaultThreadCurrentUICulture = turkish;

var builder = WebAssemblyHostBuilder.CreateDefault(args);
builder.RootComponents.Add<App>("#app");
builder.RootComponents.Add<HeadOutlet>("head::after");

await builder.Build().RunAsync();
