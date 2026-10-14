namespace ExcelToolkit.Core.Data;

/// <summary>
/// Bellekteki tablo: sütun adları + satırlar.
/// Hücre değerleri şu türlerden biridir: null, string, double, bool, DateTime, TimeSpan.
/// (v1'deki pandas DataFrame'in yerine geçen basit model.)
/// </summary>
public sealed class SheetData
{
    public SheetData(string name, IReadOnlyList<string> columns, IReadOnlyList<object?[]> rows)
    {
        ArgumentNullException.ThrowIfNull(columns);
        ArgumentNullException.ThrowIfNull(rows);

        for (var i = 0; i < rows.Count; i++)
        {
            if (rows[i].Length != columns.Count)
            {
                throw new ArgumentException(
                    $"Satır {i + 1}: {rows[i].Length} hücre var, {columns.Count} bekleniyordu.",
                    nameof(rows));
            }
        }

        Name = name ?? string.Empty;
        Columns = columns;
        Rows = rows;
    }

    /// <summary>Sayfa ya da dosya adı.</summary>
    public string Name { get; }

    public IReadOnlyList<string> Columns { get; }

    public IReadOnlyList<object?[]> Rows { get; }

    public int RowCount => Rows.Count;

    public int ColumnCount => Columns.Count;

    public static SheetData Empty(string name) => new(name, Array.Empty<string>(), Array.Empty<object?[]>());

    /// <summary>Aynı sütunlarla yeni satır listesi içeren bir kopya döner.</summary>
    public SheetData WithRows(IReadOnlyList<object?[]> rows) => new(Name, Columns, rows);
}
