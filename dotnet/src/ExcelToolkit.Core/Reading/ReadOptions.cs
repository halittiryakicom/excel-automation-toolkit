namespace ExcelToolkit.Core.Reading;

/// <summary>Dosya okuma ayarları.</summary>
public sealed record ReadOptions
{
    /// <summary>Okunacak sayfa adı (.xlsx). Boşsa ilk sayfa okunur.</summary>
    public string? SheetName { get; init; }

    /// <summary>
    /// En fazla veri satırı (başlık hariç). Aşılırsa <see cref="SheetTooLargeException"/> fırlatılır.
    /// Web demo sınırı 50.000 satır.
    /// </summary>
    public int MaxRows { get; init; } = 50_000;

    /// <summary>CSV ayırıcısı. Boşsa ilk satırdan otomatik bulunur (; , sekme).</summary>
    public char? CsvDelimiter { get; init; }

    /// <summary>CSV'de sayı ve tarihleri metinden çevir (varsayılan: evet).</summary>
    public bool InferCsvTypes { get; init; } = true;
}
