using ExcelToolkit.Core.Cleaning;
using ExcelToolkit.Core.Processing;
using ExcelToolkit.Core.Reading;

namespace ExcelToolkit.Core.Tests;

public class WorkbookProcessorTests
{
    private static string SamplePath => Path.Combine(AppContext.BaseDirectory, "TestData", "sample_employee_data.xlsx");

    [Fact]
    public void Sample_is_processed_like_v1()
    {
        using var stream = File.OpenRead(SamplePath);

        var result = WorkbookProcessor.Process(stream, "sample_employee_data.xlsx");

        Assert.Equal("sample_employee_data.xlsx", result.FileName);
        Assert.Equal(12, result.Before.RowCount);
        Assert.Equal(9, result.After.RowCount);
        Assert.Equal(12, result.Cleaning.OriginalRows);
        Assert.Equal(9, result.Cleaning.CurrentRows);
        Assert.Equal(38250, result.After.Columns.Single(c => c.Name == "Salary").Numeric!.Mean, 10);
    }

    [Fact]
    public void Options_are_passed_to_cleaner()
    {
        using var stream = File.OpenRead(SamplePath);

        var result = WorkbookProcessor.Process(stream, "sample_employee_data.xlsx", new CleaningOptions { RemoveEmptyRows = false, RemoveDuplicateRows = false });

        Assert.Equal(12, result.After.RowCount);
        Assert.Equal(0, result.Cleaning.RemovedEmptyRows + result.Cleaning.RemovedDuplicateRows);
    }

    [Fact]
    public void Xlsx_output_can_be_read_back()
    {
        using var stream = File.OpenRead(SamplePath);
        var result = WorkbookProcessor.Process(stream, "sample_employee_data.xlsx");

        var bytes = WorkbookProcessor.ToXlsx(result.Cleaned);
        using var reloaded = new MemoryStream(bytes);

        Assert.Equal(9, SheetReader.Read(reloaded, "temiz.xlsx").RowCount);
    }

    [Fact]
    public void Unsupported_file_is_rejected_with_turkish_message()
    {
        using var stream = new MemoryStream(new byte[] { 1, 2, 3 });

        var ex = Assert.Throws<UnsupportedFileException>(() => WorkbookProcessor.Process(stream, "makro.xlsm"));
        Assert.Contains(".xlsm", ex.Message);
    }

    [Theory]
    [InlineData("Satış Ekim.csv", "Satış Ekim_temiz.xlsx")]
    [InlineData("rapor:2026?.xlsx", "rapor_2026__temiz.xlsx")]
    [InlineData(".xlsx", "tablo_temiz.xlsx")]
    [InlineData("", "tablo_temiz.xlsx")]
    public void Output_file_name_is_safe(string input, string expected)
    {
        Assert.Equal(expected, WorkbookProcessor.OutputFileName(input));
    }
}
