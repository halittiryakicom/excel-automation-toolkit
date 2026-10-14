using System.Text;
using ExcelToolkit.Core.Data;
using ExcelToolkit.Core.Reading;

namespace ExcelToolkit.Core.Tests;

public class CsvSheetReaderTests
{
    static CsvSheetReaderTests()
    {
        Encoding.RegisterProvider(CodePagesEncodingProvider.Instance);
    }

    private static SheetData ReadText(string text, Encoding? encoding = null, ReadOptions? options = null)
        => ReadBytes((encoding ?? new UTF8Encoding(false)).GetBytes(text), options);

    private static SheetData ReadBytes(byte[] bytes, ReadOptions? options = null)
    {
        using var stream = new MemoryStream(bytes);
        return new CsvSheetReader().Read(stream, "test", options ?? new ReadOptions());
    }

    [Fact]
    public void Turkish_excel_csv_with_semicolon_and_decimal_comma()
    {
        var sheet = ReadText("Ürün;Fiyat;Şehir\r\nVida;12,50;İstanbul\r\nSomun;1.250,75;Bursa\r\n");

        Assert.Equal(new[] { "Ürün", "Fiyat", "Şehir" }, sheet.Columns);
        Assert.Equal(2, sheet.RowCount);
        Assert.Equal(12.5, sheet.Rows[0][1]);
        Assert.Equal(1250.75, sheet.Rows[1][1]);
        Assert.Equal("İstanbul", sheet.Rows[0][2]);
    }

    [Fact]
    public void Quoted_fields_with_delimiter_quote_and_newline()
    {
        var sheet = ReadText("Ad,Not\n\"Yılmaz, Ali\",\"Dedi ki \"\"tamam\"\"\nikinci satır\"\n");

        Assert.Equal(new[] { "Ad", "Not" }, sheet.Columns);
        var row = Assert.Single(sheet.Rows);
        Assert.Equal("Yılmaz, Ali", row[0]);
        Assert.Equal("Dedi ki \"tamam\"\nikinci satır", row[1]);
    }

    [Fact]
    public void Utf8_bom_is_removed_from_first_header()
    {
        var bom = new byte[] { 0xEF, 0xBB, 0xBF };
        var sheet = ReadBytes(bom.Concat(Encoding.UTF8.GetBytes("Ad;Yaş\nEce;30")).ToArray());

        Assert.Equal("Ad", sheet.Columns[0]);
    }

    [Fact]
    public void Windows_1254_file_is_decoded()
    {
        var sheet = ReadText("Şehir;İlçe\nİstanbul;Şişli\n", Encoding.GetEncoding(1254));

        Assert.Equal(new[] { "Şehir", "İlçe" }, sheet.Columns);
        Assert.Equal("Şişli", sheet.Rows[0][1]);
    }

    [Fact]
    public void Tab_delimiter_is_detected()
    {
        var sheet = ReadText("A\tB\n1\t2\n");

        Assert.Equal(new[] { "A", "B" }, sheet.Columns);
        Assert.Equal(2d, sheet.Rows[0][1]);
    }

    [Fact]
    public void Leading_blank_lines_are_skipped_and_trailing_blank_lines_are_ignored()
    {
        var sheet = ReadText("\n\nAd;Adet\nVida;5\n\n;\nSomun;3\n\n\n");

        Assert.Equal(new[] { "Ad", "Adet" }, sheet.Columns);
        // Aradaki 2 boş satır korunur (temizleme raporlasın diye), sondakiler atılır.
        Assert.Equal(4, sheet.RowCount);
        Assert.Equal("Somun", sheet.Rows[3][0]);
    }

    [Fact]
    public void Short_header_gets_generated_column_names_and_short_rows_are_padded()
    {
        var sheet = ReadText("Ad;Adet\nVida;5;fazla\nSomun\n");

        Assert.Equal(new[] { "Ad", "Adet", "Sütun 3" }, sheet.Columns);
        Assert.Equal("fazla", sheet.Rows[0][2]);
        Assert.Null(sheet.Rows[1][1]);
    }

    [Fact]
    public void Type_inference_can_be_turned_off()
    {
        var sheet = ReadText("Kod;Adet\n007;5\n", options: new ReadOptions { InferCsvTypes = false });

        Assert.Equal("5", sheet.Rows[0][1]);
    }

    [Fact]
    public void Explicit_delimiter_overrides_detection()
    {
        var sheet = ReadText("a;b,c\n1;2,3\n", options: new ReadOptions { CsvDelimiter = ',' });

        Assert.Equal(new[] { "a;b", "c" }, sheet.Columns);
    }

    [Fact]
    public void Row_limit_is_enforced()
    {
        var text = "No\n" + string.Join("\n", Enumerable.Range(1, 6)) + "\n";

        var ex = Assert.Throws<SheetTooLargeException>(() => ReadText(text, options: new ReadOptions { MaxRows = 5 }));
        Assert.Equal(6, ex.RowCount);
    }

    [Fact]
    public void Empty_file_returns_empty_table()
    {
        var sheet = ReadText("");

        Assert.Equal(0, sheet.ColumnCount);
        Assert.Equal(0, sheet.RowCount);
    }
}
