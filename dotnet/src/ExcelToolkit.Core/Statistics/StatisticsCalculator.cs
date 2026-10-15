using ExcelToolkit.Core.Cleaning;
using ExcelToolkit.Core.Data;

namespace ExcelToolkit.Core.Statistics;

/// <summary>Sütunun içerik türü (boş hücreler hesaba katılmaz).</summary>
public enum ColumnKind
{
    /// <summary>Hiç dolu hücre yok.</summary>
    Empty,
    Number,
    Text,
    Date,
    Time,
    Boolean,

    /// <summary>Birden fazla tür karışık (ör. sayı + metin).</summary>
    Mixed,
}

/// <summary>Sayısal sütun özeti. Standart sapma örneklem standart sapmasıdır (pandas std() ile aynı); 2'den az değer varsa null.</summary>
public sealed record NumericSummary(int Count, double Sum, double Mean, double Min, double Max, double Median, double? StandardDeviation);

public sealed record ColumnStatistics(string Name, ColumnKind Kind, int FilledCount, int EmptyCount, NumericSummary? Numeric);

/// <summary>Tablo özeti (v1'deki StatisticsEngine.generate_summary + sayısal istatistikler).</summary>
public sealed record SheetStatistics(
    int RowCount,
    int ColumnCount,
    int NumericColumnCount,
    int TextColumnCount,
    int EmptyCellCount,
    IReadOnlyList<ColumnStatistics> Columns)
{
    public IEnumerable<ColumnStatistics> NumericColumns => Columns.Where(c => c.Numeric is not null);
}

/// <summary>
/// Tabloyu değiştirmeden istatistik üretir.
/// Sayısal sütun: tüm dolu hücreleri sayı olan sütun. "Metin" sayısı, v1'deki gibi sayısal olmayan tüm sütunlardır.
/// Not: pandas tamamen boş bir sütunu sayısal sayar; burada <see cref="ColumnKind.Empty"/> olur ve sayısal sayılmaz.
/// </summary>
public static class StatisticsCalculator
{
    public static SheetStatistics Calculate(SheetData sheet)
    {
        ArgumentNullException.ThrowIfNull(sheet);

        var columns = new List<ColumnStatistics>(sheet.ColumnCount);
        var emptyCells = 0;

        for (var c = 0; c < sheet.ColumnCount; c++)
        {
            var numbers = new List<double>();
            var kinds = new HashSet<ColumnKind>();
            var empty = 0;

            foreach (var row in sheet.Rows)
            {
                var value = row[c];
                if (DataCleaner.IsEmptyCell(value))
                {
                    empty++;
                    continue;
                }

                var kind = KindOf(value!);
                kinds.Add(kind);
                if (kind == ColumnKind.Number)
                {
                    numbers.Add((double)value!);
                }
            }

            var columnKind = kinds.Count switch
            {
                0 => ColumnKind.Empty,
                1 => kinds.First(),
                _ => ColumnKind.Mixed,
            };

            var numeric = columnKind == ColumnKind.Number ? Summarize(numbers) : null;
            columns.Add(new ColumnStatistics(sheet.Columns[c], columnKind, sheet.RowCount - empty, empty, numeric));
            emptyCells += empty;
        }

        var numericCount = columns.Count(c => c.Numeric is not null);
        return new SheetStatistics(
            sheet.RowCount,
            sheet.ColumnCount,
            numericCount,
            sheet.ColumnCount - numericCount,
            emptyCells,
            columns);
    }

    internal static NumericSummary Summarize(IReadOnlyList<double> values)
    {
        var count = values.Count;
        var sum = 0d;
        var min = double.MaxValue;
        var max = double.MinValue;

        foreach (var v in values)
        {
            sum += v;
            min = Math.Min(min, v);
            max = Math.Max(max, v);
        }

        var mean = sum / count;

        var sorted = values.ToArray();
        Array.Sort(sorted);
        var median = count % 2 == 1
            ? sorted[count / 2]
            : (sorted[(count / 2) - 1] + sorted[count / 2]) / 2;

        double? std = null;
        if (count >= 2)
        {
            var squares = 0d;
            foreach (var v in values)
            {
                squares += (v - mean) * (v - mean);
            }

            std = Math.Sqrt(squares / (count - 1));
        }

        return new NumericSummary(count, sum, mean, min, max, median, std);
    }

    private static ColumnKind KindOf(object value) => value switch
    {
        double => ColumnKind.Number,
        string => ColumnKind.Text,
        DateTime => ColumnKind.Date,
        TimeSpan => ColumnKind.Time,
        bool => ColumnKind.Boolean,
        _ => ColumnKind.Mixed,
    };
}
