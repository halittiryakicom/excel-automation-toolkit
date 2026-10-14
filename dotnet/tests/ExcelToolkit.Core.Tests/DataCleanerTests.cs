using ExcelToolkit.Core.Cleaning;
using ExcelToolkit.Core.Data;

namespace ExcelToolkit.Core.Tests;

public class DataCleanerTests
{
    private static SheetData Table(params object?[][] rows) => new("test", new[] { "A", "B" }, rows);

    [Fact]
    public void Removes_rows_that_are_null_or_whitespace_only()
    {
        var sheet = Table(
            new object?[] { "x", 1d },
            new object?[] { null, null },
            new object?[] { "  ", null },
            new object?[] { null, 0d });

        var result = DataCleaner.Clean(sheet);

        Assert.Equal(2, result.Summary.RemovedEmptyRows);
        Assert.Equal(2, result.Summary.CurrentRows);
    }

    [Fact]
    public void Removes_duplicates_and_keeps_first_occurrence_in_order()
    {
        var sheet = Table(
            new object?[] { "b", 2d },
            new object?[] { "a", 1d },
            new object?[] { "b", 2d },
            new object?[] { "a", 1d },
            new object?[] { "c", 3d });

        var result = DataCleaner.Clean(sheet);

        Assert.Equal(2, result.Summary.RemovedDuplicateRows);
        Assert.Equal(new[] { "b", "a", "c" }, result.Sheet.Rows.Select(r => (string)r[0]!));
    }

    [Fact]
    public void Blank_cells_compare_equal_but_types_and_case_matter()
    {
        var sheet = Table(
            new object?[] { "x", null },
            new object?[] { "x", "" },       // boş = boş → tekrar
            new object?[] { "X", null },     // büyük harf → farklı
            new object?[] { "1", 1d },
            new object?[] { 1d, 1d });       // metin "1" ile sayı 1 farklı

        var result = DataCleaner.Clean(sheet);

        Assert.Equal(1, result.Summary.RemovedDuplicateRows);
        Assert.Equal(4, result.Summary.CurrentRows);
    }

    [Fact]
    public void Options_can_disable_steps()
    {
        var sheet = Table(
            new object?[] { null, null },
            new object?[] { "a", 1d },
            new object?[] { "a", 1d });

        var result = DataCleaner.Clean(sheet, new CleaningOptions { RemoveEmptyRows = false });

        Assert.Equal(new CleaningSummary(3, 0, 1, 2), result.Summary);
    }

    [Fact]
    public void Input_table_is_not_modified()
    {
        var sheet = Table(new object?[] { "a", 1d }, new object?[] { "a", 1d });

        DataCleaner.Clean(sheet);

        Assert.Equal(2, sheet.RowCount);
    }
}
