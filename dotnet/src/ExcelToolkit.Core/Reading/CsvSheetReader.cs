using System.Text;
using ExcelToolkit.Core.Data;

namespace ExcelToolkit.Core.Reading;

/// <summary>
/// CSV okuyucu (dış paket yok). Türkçe Excel'in kaydettiği dosyalar için:
/// ayırıcı otomatik bulunur (; , sekme), kodlama UTF-8 (BOM'lu/BOM'suz) ya da Windows-1254 olabilir,
/// tırnak içindeki virgül/satır sonu desteklenir.
/// </summary>
public sealed class CsvSheetReader : ISheetReader
{
    private static readonly char[] CandidateDelimiters = { ';', ',', '\t' };

    static CsvSheetReader()
    {
        // Windows-1254 (Türkçe) için gerekli.
        Encoding.RegisterProvider(CodePagesEncodingProvider.Instance);
    }

    public SheetData Read(Stream stream, string name, ReadOptions options)
    {
        ArgumentNullException.ThrowIfNull(stream);
        ArgumentNullException.ThrowIfNull(options);

        var text = DecodeText(stream);
        var delimiter = options.CsvDelimiter ?? DetectDelimiter(text);
        var records = ParseRecords(text, delimiter);

        // Baştaki tamamen boş satırları atla.
        var headerIndex = records.FindIndex(r => !IsBlankRecord(r));
        if (headerIndex < 0)
        {
            return SheetData.Empty(name);
        }

        // Sondaki tamamen boş satırlar (dosya sonundaki fazladan satır sonları) veri sayılmaz.
        // Aradaki boş satırlar korunur; temizleme adımı onları "boş satır" olarak raporlar.
        var lastIndex = records.FindLastIndex(r => !IsBlankRecord(r));
        records.RemoveRange(lastIndex + 1, records.Count - lastIndex - 1);

        var dataCount = records.Count - headerIndex - 1;
        if (dataCount > options.MaxRows)
        {
            throw new SheetTooLargeException(dataCount, options.MaxRows);
        }

        var header = records[headerIndex];
        var width = header.Count;
        for (var i = headerIndex + 1; i < records.Count; i++)
        {
            width = Math.Max(width, records[i].Count);
        }

        var rawNames = new string?[width];
        for (var c = 0; c < width; c++)
        {
            rawNames[c] = c < header.Count ? header[c] : null;
        }

        var columns = ColumnNames.Normalize(rawNames);
        var rows = new List<object?[]>(dataCount);

        for (var i = headerIndex + 1; i < records.Count; i++)
        {
            var record = records[i];
            var row = new object?[width];
            for (var c = 0; c < record.Count; c++)
            {
                row[c] = options.InferCsvTypes
                    ? CellValueParser.Parse(record[c])
                    : (string.IsNullOrWhiteSpace(record[c]) ? null : record[c]);
            }

            rows.Add(row);
        }

        return new SheetData(name, columns, rows);
    }

    internal static string DecodeText(Stream stream)
    {
        using var buffer = new MemoryStream();
        stream.CopyTo(buffer);
        var bytes = buffer.ToArray();

        if (bytes.Length >= 3 && bytes[0] == 0xEF && bytes[1] == 0xBB && bytes[2] == 0xBF)
        {
            return Encoding.UTF8.GetString(bytes, 3, bytes.Length - 3);
        }

        if (bytes.Length >= 2 && bytes[0] == 0xFF && bytes[1] == 0xFE)
        {
            return Encoding.Unicode.GetString(bytes, 2, bytes.Length - 2);
        }

        if (bytes.Length >= 2 && bytes[0] == 0xFE && bytes[1] == 0xFF)
        {
            return Encoding.BigEndianUnicode.GetString(bytes, 2, bytes.Length - 2);
        }

        try
        {
            // Geçersiz bayt varsa hata verir → UTF-8 değildir.
            return new UTF8Encoding(encoderShouldEmitUTF8Identifier: false, throwOnInvalidBytes: true).GetString(bytes);
        }
        catch (DecoderFallbackException)
        {
            return Encoding.GetEncoding(1254).GetString(bytes);
        }
    }

    /// <summary>İlk kaydın (tırnak dışındaki) karakterlerine bakarak en sık geçen ayırıcıyı seçer.</summary>
    internal static char DetectDelimiter(string text)
    {
        var counts = new int[CandidateDelimiters.Length];
        var inQuotes = false;

        foreach (var ch in text)
        {
            if (ch == '"')
            {
                inQuotes = !inQuotes;
                continue;
            }

            if (!inQuotes && (ch == '\n' || ch == '\r'))
            {
                if (counts.Any(c => c > 0))
                {
                    break;
                }

                continue; // baştaki boş satırlar
            }

            if (!inQuotes)
            {
                var index = Array.IndexOf(CandidateDelimiters, ch);
                if (index >= 0)
                {
                    counts[index]++;
                }
            }
        }

        var best = 0;
        for (var i = 1; i < counts.Length; i++)
        {
            if (counts[i] > counts[best])
            {
                best = i;
            }
        }

        return counts[best] > 0 ? CandidateDelimiters[best] : ',';
    }

    /// <summary>RFC 4180'e uygun ayrıştırma: "" kaçış, tırnak içinde ayırıcı ve satır sonu.</summary>
    internal static List<List<string>> ParseRecords(string text, char delimiter)
    {
        var records = new List<List<string>>();
        var record = new List<string>();
        var field = new StringBuilder();
        var inQuotes = false;
        var fieldStarted = false;

        for (var i = 0; i < text.Length; i++)
        {
            var ch = text[i];

            if (inQuotes)
            {
                if (ch == '"')
                {
                    if (i + 1 < text.Length && text[i + 1] == '"')
                    {
                        field.Append('"');
                        i++;
                    }
                    else
                    {
                        inQuotes = false;
                    }
                }
                else
                {
                    field.Append(ch);
                }

                continue;
            }

            if (ch == '"' && field.Length == 0)
            {
                inQuotes = true;
                fieldStarted = true;
            }
            else if (ch == delimiter)
            {
                record.Add(field.ToString());
                field.Clear();
                fieldStarted = true;
            }
            else if (ch == '\r' || ch == '\n')
            {
                if (ch == '\r' && i + 1 < text.Length && text[i + 1] == '\n')
                {
                    i++;
                }

                record.Add(field.ToString());
                field.Clear();
                records.Add(record);
                record = new List<string>();
                fieldStarted = false;
            }
            else
            {
                field.Append(ch);
                fieldStarted = true;
            }
        }

        // Dosya satır sonuyla bitmiyorsa son kaydı ekle.
        if (fieldStarted || field.Length > 0 || record.Count > 0)
        {
            record.Add(field.ToString());
            records.Add(record);
        }

        return records;
    }

    private static bool IsBlankRecord(List<string> record) => record.All(string.IsNullOrWhiteSpace);
}
