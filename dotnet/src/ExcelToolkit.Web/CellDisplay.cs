using ExcelToolkit.Core.Statistics;

namespace ExcelToolkit.Web;

/// <summary>Hücre değerlerini ve sütun türlerini ekranda Türkçe gösterir.</summary>
public static class CellDisplay
{
    public static string Format(object? value) => value switch
    {
        null => string.Empty,
        string s => s,
        double d => d.ToString("#,##0.##"),
        bool b => b ? "Evet" : "Hayır",
        DateTime dt when dt.TimeOfDay == TimeSpan.Zero => dt.ToString("dd.MM.yyyy"),
        DateTime dt => dt.ToString("dd.MM.yyyy HH:mm"),
        TimeSpan ts => ts.ToString(@"hh\:mm"),
        _ => value.ToString() ?? string.Empty,
    };

    public static string Number(double? value) => value is null ? "–" : value.Value.ToString("#,##0.##");

    public static string Kind(ColumnKind kind) => kind switch
    {
        ColumnKind.Empty => "Boş",
        ColumnKind.Number => "Sayı",
        ColumnKind.Text => "Metin",
        ColumnKind.Date => "Tarih",
        ColumnKind.Time => "Saat",
        ColumnKind.Boolean => "Evet/Hayır",
        ColumnKind.Mixed => "Karışık",
        _ => kind.ToString(),
    };
}
