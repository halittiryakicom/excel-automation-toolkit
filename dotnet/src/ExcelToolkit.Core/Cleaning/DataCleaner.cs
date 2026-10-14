using ExcelToolkit.Core.Data;

namespace ExcelToolkit.Core.Cleaning;

/// <summary>Temizleme ayarları.</summary>
public sealed record CleaningOptions
{
    public static readonly CleaningOptions Default = new();

    /// <summary>Tüm hücreleri boş (ya da sadece boşluk) olan satırları sil.</summary>
    public bool RemoveEmptyRows { get; init; } = true;

    /// <summary>Tekrarlanan satırları sil (ilki kalır).</summary>
    public bool RemoveDuplicateRows { get; init; } = true;
}

/// <summary>Temizleme özeti (v1'deki get_summary ile aynı alanlar).</summary>
public sealed record CleaningSummary(int OriginalRows, int RemovedEmptyRows, int RemovedDuplicateRows, int CurrentRows);

public sealed record CleaningResult(SheetData Sheet, CleaningSummary Summary);

/// <summary>
/// Boş ve tekrarlanan satırları temizler. Girdi tabloyu değiştirmez, yeni tablo döner.
/// Sıra v1 ile aynı: önce boş satırlar, sonra tekrarlar.
/// </summary>
public static class DataCleaner
{
    public static CleaningResult Clean(SheetData sheet, CleaningOptions? options = null)
    {
        ArgumentNullException.ThrowIfNull(sheet);
        options ??= CleaningOptions.Default;

        IReadOnlyList<object?[]> rows = sheet.Rows;
        var removedEmpty = 0;
        var removedDuplicates = 0;

        if (options.RemoveEmptyRows)
        {
            var kept = rows.Where(r => !IsEmptyRow(r)).ToList();
            removedEmpty = rows.Count - kept.Count;
            rows = kept;
        }

        if (options.RemoveDuplicateRows)
        {
            var seen = new HashSet<object?[]>(RowComparer.Instance);
            var kept = new List<object?[]>(rows.Count);
            foreach (var row in rows)
            {
                if (seen.Add(row))
                {
                    kept.Add(row);
                }
            }

            removedDuplicates = rows.Count - kept.Count;
            rows = kept;
        }

        var cleaned = sheet.WithRows(rows);
        var summary = new CleaningSummary(sheet.RowCount, removedEmpty, removedDuplicates, cleaned.RowCount);
        return new CleaningResult(cleaned, summary);
    }

    public static bool IsEmptyRow(object?[] row) => row.All(IsEmptyCell);

    public static bool IsEmptyCell(object? value) => value is null || (value is string s && string.IsNullOrWhiteSpace(s));
}

/// <summary>
/// Satırları hücre hücre karşılaştırır. Boş hücre (null ya da boşluk) birbirine eşittir.
/// Metin karşılaştırması büyük/küçük harfe duyarlıdır (pandas drop_duplicates ile aynı).
/// </summary>
internal sealed class RowComparer : IEqualityComparer<object?[]>
{
    public static readonly RowComparer Instance = new();

    public bool Equals(object?[]? x, object?[]? y)
    {
        if (ReferenceEquals(x, y))
        {
            return true;
        }

        if (x is null || y is null || x.Length != y.Length)
        {
            return false;
        }

        for (var i = 0; i < x.Length; i++)
        {
            if (!CellEquals(x[i], y[i]))
            {
                return false;
            }
        }

        return true;
    }

    public int GetHashCode(object?[] row)
    {
        var hash = new HashCode();
        foreach (var cell in row)
        {
            hash.Add(CellHash(cell));
        }

        return hash.ToHashCode();
    }

    private static bool CellEquals(object? a, object? b)
    {
        var aEmpty = DataCleaner.IsEmptyCell(a);
        var bEmpty = DataCleaner.IsEmptyCell(b);
        if (aEmpty || bEmpty)
        {
            return aEmpty && bEmpty;
        }

        if (a is string sa && b is string sb)
        {
            return string.Equals(sa, sb, StringComparison.Ordinal);
        }

        return a!.Equals(b);
    }

    private static int CellHash(object? cell) => cell switch
    {
        null => 0,
        string s when string.IsNullOrWhiteSpace(s) => 0,
        string s => StringComparer.Ordinal.GetHashCode(s),
        _ => cell.GetHashCode(),
    };
}
