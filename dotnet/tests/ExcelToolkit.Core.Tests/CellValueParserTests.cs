using ExcelToolkit.Core.Reading;

namespace ExcelToolkit.Core.Tests;

public class CellValueParserTests
{
    [Theory]
    [InlineData("42", 42d)]
    [InlineData("-12.5", -12.5)]
    [InlineData("12,5", 12.5)]
    [InlineData("1.250,75", 1250.75)]
    [InlineData("1.234.567", 1234567d)]
    [InlineData(" 7 ", 7d)]
    [InlineData("0", 0d)]
    [InlineData("0,5", 0.5)]
    public void Numbers(string raw, double expected)
    {
        Assert.Equal(expected, CellValueParser.Parse(raw));
    }

    [Theory]
    [InlineData("007")]          // ürün kodu
    [InlineData("06100")]        // posta kodu
    [InlineData("M8x20")]
    [InlineData("12,5 kg")]
    [InlineData("1,2,3")]
    public void Text_stays_text(string raw)
    {
        Assert.Equal(raw, CellValueParser.Parse(raw));
    }

    [Theory]
    [InlineData(null)]
    [InlineData("")]
    [InlineData("   ")]
    public void Blank_is_null(string? raw)
    {
        Assert.Null(CellValueParser.Parse(raw));
    }

    [Fact]
    public void Dates()
    {
        Assert.Equal(new DateTime(2026, 10, 16), CellValueParser.Parse("16.10.2026"));
        Assert.Equal(new DateTime(2026, 10, 16), CellValueParser.Parse("2026-10-16"));
        Assert.Equal(new DateTime(2026, 10, 16, 18, 0, 0), CellValueParser.Parse("16.10.2026 18:00"));
    }
}
