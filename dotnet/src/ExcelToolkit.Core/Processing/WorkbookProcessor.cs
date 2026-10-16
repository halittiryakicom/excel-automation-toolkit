using ExcelToolkit.Core.Cleaning;
using ExcelToolkit.Core.Data;
using ExcelToolkit.Core.Reading;
using ExcelToolkit.Core.Statistics;
using ExcelToolkit.Core.Writing;

namespace ExcelToolkit.Core.Processing;

/// <summary>Bir dosyanın tek seferde işlenmesinin sonucu: temiz tablo + temizlik özeti + önce/sonra istatistikleri.</summary>
public sealed record ProcessResult(
    string FileName,
    SheetData Cleaned,
    CleaningSummary Cleaning,
    SheetStatistics Before,
    SheetStatistics After);

/// <summary>
/// Oku → istatistik → temizle → istatistik akışı. Web demo, ileride API ve masaüstü aynı akışı kullanır.
/// Tümü bellekte çalışır; diske bir şey yazılmaz.
/// </summary>
public static class WorkbookProcessor
{
    /// <summary>Web demo dosya sınırı: 10 MB.</summary>
    public const long MaxFileSizeBytes = 10 * 1024 * 1024;

    /// <summary>Web demo satır sınırı: 50.000.</summary>
    public const int MaxRows = 50_000;

    public static ProcessResult Process(Stream content, string fileName, CleaningOptions? options = null)
    {
        ArgumentNullException.ThrowIfNull(content);
        ArgumentException.ThrowIfNullOrWhiteSpace(fileName);

        var sheet = SheetReader.Read(content, fileName, new ReadOptions { MaxRows = MaxRows });
        var before = StatisticsCalculator.Calculate(sheet);
        var cleaned = DataCleaner.Clean(sheet, options);
        var after = StatisticsCalculator.Calculate(cleaned.Sheet);

        return new ProcessResult(Path.GetFileName(fileName), cleaned.Sheet, cleaned.Summary, before, after);
    }

    /// <summary>Tabloyu .xlsx olarak bellekte üretir.</summary>
    public static byte[] ToXlsx(SheetData sheet)
    {
        ArgumentNullException.ThrowIfNull(sheet);
        using var output = new MemoryStream();
        XlsxSheetWriter.Write(sheet, output);
        return output.ToArray();
    }

    /// <summary>"Satış Ekim.csv" → "Satış Ekim_temiz.xlsx". Geçersiz karakterler "_" olur, ad en fazla 80 karakter.</summary>
    public static string OutputFileName(string fileName)
    {
        var name = Path.GetFileNameWithoutExtension(fileName ?? string.Empty).Trim();
        var invalid = Path.GetInvalidFileNameChars().Concat(new[] { '/', '\\', ':', '*', '?', '"', '<', '>', '|' }).ToHashSet();
        name = new string(name.Select(c => invalid.Contains(c) || char.IsControl(c) ? '_' : c).ToArray()).Trim('.', ' ');

        if (name.Length == 0)
        {
            name = "tablo";
        }

        if (name.Length > 80)
        {
            name = name[..80];
        }

        return $"{name}_temiz.xlsx";
    }
}
