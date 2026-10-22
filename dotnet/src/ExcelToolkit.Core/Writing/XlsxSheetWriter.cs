using System.Globalization;
using ClosedXML.Excel;
using ExcelToolkit.Core.Data;

namespace ExcelToolkit.Core.Writing;

/// <summary>
/// Tabloyu .xlsx olarak kaydeder (v1'deki save_excel).
/// Başlık satırı kalın ve sabit, filtre açık, sütun genişlikleri ilk 200 satıra göre ayarlı.
/// "=" ile başlayan metinler formül olarak değil metin olarak yazılır.
/// </summary>
public static class XlsxSheetWriter
{
    private const int MaxSheetNameLength = 31;
    private const int WidthSampleRows = 200;
    private static readonly char[] InvalidSheetNameChars = { '[', ']', ':', '*', '?', '/', '\\' };

    public static void Save(SheetData sheet, string path)
    {
        ArgumentException.ThrowIfNullOrWhiteSpace(path);

        var directory = Path.GetDirectoryName(Path.GetFullPath(path));
        if (!string.IsNullOrEmpty(directory))
        {
            Directory.CreateDirectory(directory);
        }

        using var stream = File.Create(path);
        Write(sheet, stream);
    }

    public static void Write(SheetData sheet, Stream output)
    {
        ArgumentNullException.ThrowIfNull(sheet);
        ArgumentNullException.ThrowIfNull(output);

        using var workbook = new XLWorkbook();
        var ws = workbook.AddWorksheet(SafeSheetName(sheet.Name));

        for (var c = 0; c < sheet.ColumnCount; c++)
        {
            ws.Cell(1, c + 1).Value = sheet.Columns[c];
        }

        for (var r = 0; r < sheet.RowCount; r++)
        {
            var row = sheet.Rows[r];
            for (var c = 0; c < sheet.ColumnCount; c++)
            {
                SetValue(ws.Cell(r + 2, c + 1), row[c]);
            }
        }

        if (sheet.ColumnCount > 0)
        {
            ws.Row(1).Style.Font.Bold = true;
            ws.SheetView.FreezeRows(1);
            ws.Range(1, 1, sheet.RowCount + 1, sheet.ColumnCount).SetAutoFilter();
            SetColumnWidths(ws, sheet);
        }

        workbook.SaveAs(output);
    }

    private static void SetColumnWidths(IXLWorksheet ws, SheetData sheet)
    {
        var lastRow = Math.Min(sheet.RowCount + 1, WidthSampleRows);
        try
        {
            ws.Columns(1, sheet.ColumnCount).AdjustToContents(1, lastRow);
        }
        catch (Exception)
        {
            // Yazı tipi ölçümü yapılamayan ortamlar (ör. tarayıcıda WebAssembly): karakter sayısına göre yaklaşık genişlik
            for (var c = 1; c <= sheet.ColumnCount; c++)
            {
                var longest = 0;
                for (var r = 1; r <= lastRow; r++)
                {
                    longest = Math.Max(longest, ws.Cell(r, c).GetFormattedString().Length);
                }

                ws.Column(c).Width = Math.Clamp(longest + 2, 8, 60);
            }
        }
    }

    private static void SetValue(IXLCell cell, object? value)
    {
        switch (value)
        {
            case null:
                return;
            case string s:
                cell.Value = s; // metin olarak; formül çalıştırılmaz
                break;
            case double d:
                cell.Value = d;
                break;
            case bool b:
                cell.Value = b;
                break;
            case DateTime dt:
                cell.Value = dt;
                cell.Style.DateFormat.Format = dt.TimeOfDay == TimeSpan.Zero ? "dd.mm.yyyy" : "dd.mm.yyyy hh:mm";
                break;
            case TimeSpan ts:
                cell.Value = ts;
                break;
            default:
                cell.Value = Convert.ToString(value, CultureInfo.InvariantCulture) ?? string.Empty;
                break;
        }
    }

    /// <summary>Excel sayfa adı kuralları: en fazla 31 karakter, [ ] : * ? / \ yok, tek tırnakla başlayıp bitmez.</summary>
    internal static string SafeSheetName(string? name)
    {
        var chars = (name ?? string.Empty)
            .Select(ch => Array.IndexOf(InvalidSheetNameChars, ch) >= 0 ? '_' : ch)
            .ToArray();

        var safe = new string(chars).Trim().Trim('\'');
        if (safe.Length > MaxSheetNameLength)
        {
            safe = safe[..MaxSheetNameLength];
        }

        return safe.Length == 0 ? "Sayfa1" : safe;
    }
}
