using ExcelToolkit.Core.Data;

namespace ExcelToolkit.Core.Reading;

/// <summary>Bir dosya biçimini <see cref="SheetData"/>'ya çeviren okuyucu.</summary>
public interface ISheetReader
{
    /// <param name="stream">Okunacak içerik (konumu değiştirilebilir/seekable olmalı).</param>
    /// <param name="name">Tablo adı (genelde dosya adı).</param>
    /// <param name="options">Okuma ayarları.</param>
    SheetData Read(Stream stream, string name, ReadOptions options);
}
