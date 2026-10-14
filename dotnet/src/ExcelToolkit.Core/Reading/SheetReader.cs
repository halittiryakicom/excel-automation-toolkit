using ExcelToolkit.Core.Data;

namespace ExcelToolkit.Core.Reading;

/// <summary>
/// Giriş noktası: dosya uzantısına göre doğru okuyucuyu seçer.
/// Desteklenen: .xlsx, .csv · Reddedilen: .xlsm (makro), .xls (M1'de yok; ExcelDataReader ile eklenecek).
/// </summary>
public static class SheetReader
{
    public static readonly IReadOnlyList<string> SupportedExtensions = new[] { ".xlsx", ".csv" };

    public static SheetData Read(string path, ReadOptions? options = null)
    {
        ArgumentException.ThrowIfNullOrWhiteSpace(path);

        if (!File.Exists(path))
        {
            throw new FileReadException($"Dosya bulunamadı: {path}");
        }

        using var stream = File.OpenRead(path);
        return Read(stream, Path.GetFileName(path), options);
    }

    public static SheetData Read(Stream stream, string fileName, ReadOptions? options = null)
    {
        ArgumentNullException.ThrowIfNull(stream);
        ArgumentException.ThrowIfNullOrWhiteSpace(fileName);
        options ??= new ReadOptions();

        var reader = GetReader(Path.GetExtension(fileName));
        var name = Path.GetFileNameWithoutExtension(fileName);

        if (stream.CanSeek)
        {
            return reader.Read(stream, name, options);
        }

        // Web yüklemesi gibi geri sarılamayan akışlar belleğe alınır.
        using var buffer = new MemoryStream();
        stream.CopyTo(buffer);
        buffer.Position = 0;
        return reader.Read(buffer, name, options);
    }

    internal static ISheetReader GetReader(string extension)
    {
        var ext = (extension ?? string.Empty).ToLowerInvariant();

        return ext switch
        {
            ".xlsx" => new XlsxSheetReader(),
            ".csv" => new CsvSheetReader(),
            ".xlsm" => throw new UnsupportedFileException(
                "Makro içeren dosyalar (.xlsm) güvenlik nedeniyle kabul edilmiyor. Dosyayı .xlsx olarak kaydedip tekrar deneyin."),
            ".xls" => throw new UnsupportedFileException(
                "Eski Excel biçimi (.xls) henüz desteklenmiyor. Dosyayı Excel'de .xlsx olarak kaydedip tekrar deneyin."),
            _ => throw new UnsupportedFileException(
                $"Desteklenmeyen dosya türü ({(ext.Length == 0 ? "uzantısız" : ext)}). .xlsx ya da .csv dosyası yükleyin."),
        };
    }
}
