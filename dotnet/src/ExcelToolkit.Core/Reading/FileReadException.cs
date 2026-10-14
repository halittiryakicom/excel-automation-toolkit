namespace ExcelToolkit.Core.Reading;

/// <summary>Dosya okunamadığında fırlatılır. Mesaj kullanıcıya gösterilebilir (Türkçe).</summary>
public class FileReadException : Exception
{
    public FileReadException(string message)
        : base(message)
    {
    }

    public FileReadException(string message, Exception innerException)
        : base(message, innerException)
    {
    }
}

/// <summary>Dosya türü desteklenmiyor (.xlsm, .xls, diğer).</summary>
public sealed class UnsupportedFileException : FileReadException
{
    public UnsupportedFileException(string message)
        : base(message)
    {
    }
}

/// <summary>Satır sınırı aşıldı.</summary>
public sealed class SheetTooLargeException : FileReadException
{
    public SheetTooLargeException(int rowCount, int maxRows)
        : base($"Dosyada {rowCount:N0} satır var; en fazla {maxRows:N0} satır işlenebiliyor.")
    {
        RowCount = rowCount;
        MaxRows = maxRows;
    }

    public int RowCount { get; }

    public int MaxRows { get; }
}
