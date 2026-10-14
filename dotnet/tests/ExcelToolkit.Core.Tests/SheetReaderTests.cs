using System.Text;
using ExcelToolkit.Core.Reading;

namespace ExcelToolkit.Core.Tests;

public class SheetReaderTests
{
    [Theory]
    [InlineData("rapor.xlsm", "Makro")]
    [InlineData("eski.xls", ".xls")]
    [InlineData("notlar.txt", ".txt")]
    [InlineData("uzantisiz", "uzantısız")]
    public void Unsupported_files_are_rejected_with_turkish_message(string fileName, string expectedInMessage)
    {
        using var stream = new MemoryStream(new byte[] { 1, 2, 3 });

        var ex = Assert.Throws<UnsupportedFileException>(() => SheetReader.Read(stream, fileName));
        Assert.Contains(expectedInMessage, ex.Message);
    }

    [Fact]
    public void Extension_check_is_case_insensitive()
    {
        using var stream = new MemoryStream(Encoding.UTF8.GetBytes("A;B\n1;2\n"));

        var sheet = SheetReader.Read(stream, "VERI.CSV");

        Assert.Equal("VERI", sheet.Name);
        Assert.Equal(1, sheet.RowCount);
    }

    [Fact]
    public void Non_seekable_stream_is_supported()
    {
        using var inner = new MemoryStream(Encoding.UTF8.GetBytes("A;B\n1;2\n"));
        using var stream = new NonSeekableStream(inner);

        var sheet = SheetReader.Read(stream, "upload.csv");

        Assert.Equal(new[] { "A", "B" }, sheet.Columns);
    }

    [Fact]
    public void Missing_file_gives_friendly_error()
    {
        var ex = Assert.Throws<FileReadException>(() => SheetReader.Read(Path.Combine(Path.GetTempPath(), "yok-12345.xlsx")));
        Assert.Contains("bulunamadı", ex.Message);
    }

    /// <summary>Web yüklemesini taklit eder: geri sarılamayan akış.</summary>
    private sealed class NonSeekableStream(Stream inner) : Stream
    {
        public override bool CanRead => true;
        public override bool CanSeek => false;
        public override bool CanWrite => false;
        public override long Length => throw new NotSupportedException();
        public override long Position { get => throw new NotSupportedException(); set => throw new NotSupportedException(); }
        public override void Flush() { }
        public override int Read(byte[] buffer, int offset, int count) => inner.Read(buffer, offset, count);
        public override long Seek(long offset, SeekOrigin origin) => throw new NotSupportedException();
        public override void SetLength(long value) => throw new NotSupportedException();
        public override void Write(byte[] buffer, int offset, int count) => throw new NotSupportedException();
    }
}
