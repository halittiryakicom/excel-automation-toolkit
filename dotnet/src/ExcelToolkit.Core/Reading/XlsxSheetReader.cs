using System.Globalization;
using ClosedXML.Excel;
using ExcelToolkit.Core.Data;

namespace ExcelToolkit.Core.Reading;

/// <summary>
/// .xlsx okuyucu (ClosedXML). İlk dolu satır başlık kabul edilir.
/// Formüller çalıştırılmaz: dosyada kayıtlı son hesaplanmış değer okunur.
/// </summary>
public sealed class XlsxSheetReader : ISheetReader
{
    public SheetData Read(Stream stream, string name, ReadOptions options)
    {
        ArgumentNullException.ThrowIfNull(stream);
        ArgumentNullException.ThrowIfNull(options);

        XLWorkbook workbook;
        try
        {
            workbook = new XLWorkbook(stream);
        }
        catch (Exception ex) when (ex is not OutOfMemoryException)
        {
            throw new FileReadException(
                "Dosya Excel (.xlsx) olarak açılamadı. Dosya bozuk ya da farklı bir biçimde olabilir.", ex);
        }

        using (workbook)
        {
            var sheet = SelectSheet(workbook, options.SheetName);
            var used = sheet.RangeUsed(XLCellsUsedOptions.Contents);
            if (used is null)
            {
                return SheetData.Empty(sheet.Name);
            }

            var firstRow = used.RangeAddress.FirstAddress.RowNumber;
            var lastRow = used.RangeAddress.LastAddress.RowNumber;
            var firstCol = used.RangeAddress.FirstAddress.ColumnNumber;
            var lastCol = used.RangeAddress.LastAddress.ColumnNumber;
            var width = lastCol - firstCol + 1;

            var dataCount = lastRow - firstRow;
            if (dataCount > options.MaxRows)
            {
                throw new SheetTooLargeException(dataCount, options.MaxRows);
            }

            var rawNames = new string?[width];
            for (var c = 0; c < width; c++)
            {
                rawNames[c] = Convert.ToString(ToValue(sheet.Cell(firstRow, firstCol + c)), CultureInfo.InvariantCulture);
            }

            var rows = new List<object?[]>(dataCount);
            for (var r = firstRow + 1; r <= lastRow; r++)
            {
                var row = new object?[width];
                for (var c = 0; c < width; c++)
                {
                    row[c] = ToValue(sheet.Cell(r, firstCol + c));
                }

                rows.Add(row);
            }

            return new SheetData(sheet.Name, ColumnNames.Normalize(rawNames), rows);
        }
    }

    private static IXLWorksheet SelectSheet(XLWorkbook workbook, string? sheetName)
    {
        if (string.IsNullOrWhiteSpace(sheetName))
        {
            return workbook.Worksheets.First();
        }

        if (workbook.Worksheets.TryGetWorksheet(sheetName, out var sheet))
        {
            return sheet;
        }

        var names = string.Join(", ", workbook.Worksheets.Select(w => w.Name));
        throw new FileReadException($"\"{sheetName}\" adlı sayfa bulunamadı. Dosyadaki sayfalar: {names}.");
    }

    /// <summary>Hücre değerini modeldeki türlere çevirir.</summary>
    internal static object? ToValue(IXLCell cell)
    {
        var value = cell.HasFormula ? cell.CachedValue : cell.Value;

        switch (value.Type)
        {
            case XLDataType.Blank:
                return null;
            case XLDataType.Boolean:
                return value.GetBoolean();
            case XLDataType.Number:
                return value.GetNumber();
            case XLDataType.DateTime:
                return value.GetDateTime();
            case XLDataType.TimeSpan:
                return value.GetTimeSpan();
            case XLDataType.Text:
                var text = value.GetText();
                return string.IsNullOrWhiteSpace(text) ? null : text;
            default:
                // Hata değerleri (#DIV/0! vb.) metin olarak korunur.
                return value.ToString();
        }
    }
}
