using ClosedXML.Excel;
using ExcelToolkit.Core.Cleaning;
using ExcelToolkit.Core.Data;
using ExcelToolkit.Core.Reading;
using ExcelToolkit.Core.Writing;

namespace ExcelToolkit.Core.Tests;

public class XlsxSheetWriterTests
{
    private static SheetData RoundTrip(SheetData sheet)
    {
        using var stream = new MemoryStream();
        XlsxSheetWriter.Write(sheet, stream);
        stream.Position = 0;
        return new XlsxSheetReader().Read(stream, "test", new ReadOptions());
    }

    [Fact]
    public void Cleaned_sample_survives_save_and_reload()
    {
        var cleaned = DataCleaner.Clean(SheetReader.Read(Path.Combine(AppContext.BaseDirectory, "TestData", "sample_employee_data.xlsx"))).Sheet;

        var reloaded = RoundTrip(cleaned);

        Assert.Equal("Employees", reloaded.Name);
        Assert.Equal(cleaned.Columns, reloaded.Columns);
        Assert.Equal(9, reloaded.RowCount);
        for (var r = 0; r < cleaned.RowCount; r++)
        {
            Assert.Equal(cleaned.Rows[r], reloaded.Rows[r]);
        }
    }

    [Fact]
    public void Types_round_trip_and_formula_like_text_stays_text()
    {
        var sheet = new SheetData(
            "Veri",
            new[] { "Metin", "Sayı", "Tarih", "Evet", "Boş" },
            new[] { new object?[] { "=1+1", 12.5, new DateTime(2026, 10, 15, 18, 30, 0), true, null } });

        var row = Assert.Single(RoundTrip(sheet).Rows);

        Assert.Equal("=1+1", row[0]);
        Assert.Equal(12.5, row[1]);
        Assert.Equal(new DateTime(2026, 10, 15, 18, 30, 0), row[2]);
        Assert.True(row[3] is true);
        Assert.Null(row[4]);
    }

    [Fact]
    public void Header_is_bold_and_frozen()
    {
        var sheet = new SheetData("Veri", new[] { "A" }, new[] { new object?[] { 1d } });
        using var stream = new MemoryStream();
        XlsxSheetWriter.Write(sheet, stream);
        stream.Position = 0;

        using var workbook = new XLWorkbook(stream);
        var ws = workbook.Worksheet(1);

        Assert.True(ws.Cell(1, 1).Style.Font.Bold);
        Assert.Equal(1, ws.SheetView.SplitRow);
        Assert.False(ws.Cell(1, 1).HasFormula);
    }

    [Fact]
    public void Save_creates_missing_folder()
    {
        var folder = Path.Combine(Path.GetTempPath(), "ExcelToolkitTests", Guid.NewGuid().ToString("N"));
        var path = Path.Combine(folder, "cikti.xlsx");
        try
        {
            XlsxSheetWriter.Save(new SheetData("Veri", new[] { "A" }, new[] { new object?[] { "x" } }), path);

            Assert.True(File.Exists(path));
            Assert.Equal("x", SheetReader.Read(path).Rows[0][0]);
        }
        finally
        {
            if (Directory.Exists(folder))
            {
                Directory.Delete(folder, recursive: true);
            }
        }
    }

    [Theory]
    [InlineData("Satış [2026/10]", "Satış _2026_10_")]
    [InlineData("", "Sayfa1")]
    [InlineData("'tırnak'", "tırnak")]
    [InlineData("Bu sayfa adı otuz bir karakterden çok daha uzun", "Bu sayfa adı otuz bir karakterd")]
    public void Sheet_names_are_made_safe(string input, string expected)
    {
        Assert.Equal(expected, XlsxSheetWriter.SafeSheetName(input));
    }
}
