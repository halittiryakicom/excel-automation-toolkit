using ClosedXML.Excel;
using ExcelToolkit.Core.Reading;

namespace ExcelToolkit.Core.Tests;

public class XlsxSheetReaderTests
{
    private static MemoryStream Build(Action<XLWorkbook> fill)
    {
        using var workbook = new XLWorkbook();
        fill(workbook);
        var stream = new MemoryStream();
        workbook.SaveAs(stream);
        stream.Position = 0;
        return stream;
    }

    [Fact]
    public void Reads_types_and_normalizes_header()
    {
        using var stream = Build(wb =>
        {
            var ws = wb.AddWorksheet("Veri");
            ws.Cell(1, 1).Value = "Ürün";
            ws.Cell(1, 2).Value = "";          // boş başlık
            ws.Cell(1, 3).Value = "Ürün";      // tekrar eden başlık
            ws.Cell(1, 4).Value = "Tarih";
            ws.Cell(2, 1).Value = "Vida M8";
            ws.Cell(2, 2).Value = 12.5;
            ws.Cell(2, 3).Value = true;
            ws.Cell(2, 4).Value = new DateTime(2026, 10, 16);
        });

        var sheet = new XlsxSheetReader().Read(stream, "test", new ReadOptions());

        Assert.Equal("Veri", sheet.Name);
        Assert.Equal(new[] { "Ürün", "Sütun 2", "Ürün (2)", "Tarih" }, sheet.Columns);
        var row = Assert.Single(sheet.Rows);
        Assert.Equal("Vida M8", row[0]);
        Assert.Equal(12.5, row[1]);
        Assert.True(row[2] is true);
        Assert.Equal(new DateTime(2026, 10, 16), row[3]);
    }

    [Fact]
    public void Table_not_starting_at_A1_is_read_from_first_used_cell()
    {
        using var stream = Build(wb =>
        {
            var ws = wb.AddWorksheet("Sayfa1");
            ws.Cell(3, 2).Value = "Ad";
            ws.Cell(3, 3).Value = "Adet";
            ws.Cell(4, 2).Value = "Somun";
            ws.Cell(4, 3).Value = 40d;
        });

        var sheet = new XlsxSheetReader().Read(stream, "test", new ReadOptions());

        Assert.Equal(new[] { "Ad", "Adet" }, sheet.Columns);
        Assert.Equal(40d, Assert.Single(sheet.Rows)[1]);
    }

    [Fact]
    public void Reads_named_sheet_and_reports_missing_sheet()
    {
        using var stream = Build(wb =>
        {
            wb.AddWorksheet("Ocak").Cell(1, 1).Value = "A";
            wb.AddWorksheet("Şubat").Cell(1, 1).Value = "B";
        });

        var sheet = new XlsxSheetReader().Read(stream, "test", new ReadOptions { SheetName = "Şubat" });
        Assert.Equal(new[] { "B" }, sheet.Columns);

        stream.Position = 0;
        var ex = Assert.Throws<FileReadException>(
            () => new XlsxSheetReader().Read(stream, "test", new ReadOptions { SheetName = "Mart" }));
        Assert.Contains("Ocak, Şubat", ex.Message);
    }

    [Fact]
    public void Empty_sheet_returns_empty_table()
    {
        using var stream = Build(wb => wb.AddWorksheet("Boş"));

        var sheet = new XlsxSheetReader().Read(stream, "test", new ReadOptions());

        Assert.Equal(0, sheet.ColumnCount);
        Assert.Equal(0, sheet.RowCount);
    }

    [Fact]
    public void Row_limit_is_enforced()
    {
        using var stream = Build(wb =>
        {
            var ws = wb.AddWorksheet("Veri");
            ws.Cell(1, 1).Value = "No";
            for (var i = 0; i < 11; i++)
            {
                ws.Cell(i + 2, 1).Value = (double)i;
            }
        });

        var ex = Assert.Throws<SheetTooLargeException>(
            () => new XlsxSheetReader().Read(stream, "test", new ReadOptions { MaxRows = 10 }));
        Assert.Equal(11, ex.RowCount);
    }

    [Fact]
    public void Not_an_excel_file_gives_friendly_error()
    {
        using var stream = new MemoryStream("bu bir excel dosyası değil"u8.ToArray());

        var ex = Assert.Throws<FileReadException>(
            () => new XlsxSheetReader().Read(stream, "test", new ReadOptions()));
        Assert.Contains("açılamadı", ex.Message);
    }
}
