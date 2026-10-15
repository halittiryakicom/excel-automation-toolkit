using ExcelToolkit.Core.Cleaning;
using ExcelToolkit.Core.Data;
using ExcelToolkit.Core.Reading;
using ExcelToolkit.Core.Statistics;

namespace ExcelToolkit.Core.Tests;

public class StatisticsCalculatorTests
{
    private static string SamplePath => Path.Combine(AppContext.BaseDirectory, "TestData", "sample_employee_data.xlsx");

    /// <summary>
    /// Beklenen değerler v1'in pandas hesabıyla ölçüldü (14.10.2026):
    /// ham dosya → 12 satır, 2 sayısal / 3 metin sütun, 7 boş hücre;
    /// ID: toplam 58, ort. 5,2727…, std 2,6111… · Salary: toplam 378.000, ort. 37.800, medyan 37.000, std 7269,418…
    /// </summary>
    [Fact]
    public void Raw_sample_matches_v1()
    {
        var stats = StatisticsCalculator.Calculate(SheetReader.Read(SamplePath));

        Assert.Equal(12, stats.RowCount);
        Assert.Equal(5, stats.ColumnCount);
        Assert.Equal(2, stats.NumericColumnCount);
        Assert.Equal(3, stats.TextColumnCount);
        Assert.Equal(7, stats.EmptyCellCount);

        var id = stats.Columns.Single(c => c.Name == "ID").Numeric!;
        Assert.Equal(11, id.Count);
        Assert.Equal(58, id.Sum);
        Assert.Equal(5.2727272727272725, id.Mean, 10);
        Assert.Equal(1, id.Min);
        Assert.Equal(9, id.Max);
        Assert.Equal(5, id.Median);
        Assert.Equal(2.6111648393354674, id.StandardDeviation!.Value, 10);

        var salary = stats.Columns.Single(c => c.Name == "Salary").Numeric!;
        Assert.Equal(10, salary.Count);
        Assert.Equal(378000, salary.Sum);
        Assert.Equal(37800, salary.Mean, 10);
        Assert.Equal(37000, salary.Median);
        Assert.Equal(7269.418439218122, salary.StandardDeviation!.Value, 8);
    }

    [Fact]
    public void Cleaned_sample_matches_v1()
    {
        var cleaned = DataCleaner.Clean(SheetReader.Read(SamplePath)).Sheet;

        var stats = StatisticsCalculator.Calculate(cleaned);

        Assert.Equal(9, stats.RowCount);
        Assert.Equal(2, stats.EmptyCellCount);
        var salary = stats.Columns.Single(c => c.Name == "Salary").Numeric!;
        Assert.Equal(306000, salary.Sum);
        Assert.Equal(38250, salary.Mean, 10);
        Assert.Equal(8013.381665332416, salary.StandardDeviation!.Value, 8);
    }

    [Fact]
    public void Column_kinds_are_detected()
    {
        var sheet = new SheetData(
            "test",
            new[] { "Sayı", "Metin", "Tarih", "Karışık", "Boş", "Evet/Hayır" },
            new[]
            {
                new object?[] { 1d, "a", new DateTime(2026, 1, 1), 1d, null, true },
                new object?[] { 2d, "b", new DateTime(2026, 1, 2), "x", "  ", false },
            });

        var stats = StatisticsCalculator.Calculate(sheet);

        Assert.Equal(
            new[] { ColumnKind.Number, ColumnKind.Text, ColumnKind.Date, ColumnKind.Mixed, ColumnKind.Empty, ColumnKind.Boolean },
            stats.Columns.Select(c => c.Kind));
        Assert.Equal(1, stats.NumericColumnCount);
        Assert.Equal(5, stats.TextColumnCount);
        Assert.Equal(2, stats.EmptyCellCount);
    }

    [Fact]
    public void Single_value_has_no_standard_deviation_and_even_count_median_is_average()
    {
        Assert.Null(StatisticsCalculator.Summarize(new[] { 5d }).StandardDeviation);
        Assert.Equal(2.5, StatisticsCalculator.Summarize(new[] { 4d, 1d, 3d, 2d }).Median);
    }

    [Fact]
    public void Empty_table_has_zero_counts()
    {
        var stats = StatisticsCalculator.Calculate(SheetData.Empty("boş"));

        Assert.Equal(0, stats.RowCount);
        Assert.Equal(0, stats.ColumnCount);
        Assert.Empty(stats.Columns);
    }
}
