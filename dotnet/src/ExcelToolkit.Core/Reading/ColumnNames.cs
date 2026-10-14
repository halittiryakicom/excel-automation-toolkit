namespace ExcelToolkit.Core.Reading;

/// <summary>Başlık satırını kullanılabilir sütun adlarına çevirir.</summary>
internal static class ColumnNames
{
    /// <summary>
    /// Boş başlıklara "Sütun N" adı verir, tekrarlanan adlara " (2)", " (3)" ekler.
    /// Örnek: ["Ad", "", "Ad"] → ["Ad", "Sütun 2", "Ad (2)"].
    /// </summary>
    public static IReadOnlyList<string> Normalize(IReadOnlyList<string?> raw)
    {
        var result = new List<string>(raw.Count);
        var used = new HashSet<string>(StringComparer.OrdinalIgnoreCase);

        for (var i = 0; i < raw.Count; i++)
        {
            var name = raw[i]?.Trim();
            if (string.IsNullOrEmpty(name))
            {
                name = $"Sütun {i + 1}";
            }

            var candidate = name;
            var n = 2;
            while (!used.Add(candidate))
            {
                candidate = $"{name} ({n++})";
            }

            result.Add(candidate);
        }

        return result;
    }
}
