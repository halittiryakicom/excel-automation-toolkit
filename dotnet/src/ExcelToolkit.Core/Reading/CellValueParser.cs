using System.Globalization;
using System.Text.RegularExpressions;

namespace ExcelToolkit.Core.Reading;

/// <summary>
/// CSV'den gelen metni uygun türe çevirir: boş → null, sayı → double, tarih → DateTime, diğer → string.
/// </summary>
/// <remarks>
/// Kurallar (bilerek tutucu):
/// <list type="bullet">
/// <item>"1234", "-12.5" → sayı (nokta ondalık).</item>
/// <item>"12,5", "1.234,56" → sayı (Türkçe yazım: virgül ondalık, nokta binlik).</item>
/// <item>"1.234" belirsizdir; nokta ondalık sayılır → 1,234. Türkçe Excel CSV'si binlik ayırıcı yazmadığı için pratikte sorun olmaz.</item>
/// <item>"00123" gibi başında sıfır olan değerler (ürün kodu, posta kodu) metin kalır.</item>
/// <item>Tarih: "16.10.2026", "2026-10-16", isteğe bağlı saat "HH:mm" ya da "HH:mm:ss".</item>
/// </list>
/// </remarks>
public static partial class CellValueParser
{
    private static readonly string[] DateFormats =
    {
        "dd.MM.yyyy", "d.M.yyyy", "dd.MM.yyyy HH:mm", "dd.MM.yyyy HH:mm:ss", "d.M.yyyy HH:mm",
        "yyyy-MM-dd", "yyyy-MM-dd HH:mm", "yyyy-MM-dd HH:mm:ss", "yyyy-MM-dd'T'HH:mm:ss",
    };

    public static object? Parse(string? raw)
    {
        if (string.IsNullOrWhiteSpace(raw))
        {
            return null;
        }

        var text = raw.Trim();

        if (HasLeadingZero(text))
        {
            return text;
        }

        if (InvariantNumber().IsMatch(text)
            && double.TryParse(text, NumberStyles.Float, CultureInfo.InvariantCulture, out var invariant))
        {
            return invariant;
        }

        if (TurkishNumber().IsMatch(text))
        {
            var normalized = text.Replace(".", string.Empty, StringComparison.Ordinal)
                                 .Replace(',', '.');
            if (double.TryParse(normalized, NumberStyles.Float, CultureInfo.InvariantCulture, out var turkish))
            {
                return turkish;
            }
        }

        if (text.Length >= 8
            && char.IsDigit(text[0])
            && DateTime.TryParseExact(text, DateFormats, CultureInfo.InvariantCulture, DateTimeStyles.None, out var date))
        {
            return date;
        }

        return text;
    }

    /// <summary>"007", "-0012" gibi: başında sıfır olan ve hemen ardından rakam gelen değerler.</summary>
    private static bool HasLeadingZero(string text)
    {
        var start = text[0] is '+' or '-' ? 1 : 0;
        return text.Length > start + 1
               && text[start] == '0'
               && char.IsDigit(text[start + 1]);
    }

    [GeneratedRegex(@"^[+-]?\d+(\.\d+)?$")]
    private static partial Regex InvariantNumber();

    [GeneratedRegex(@"^[+-]?(\d{1,3}(\.\d{3})+(,\d+)?|\d+,\d+)$")]
    private static partial Regex TurkishNumber();
}
