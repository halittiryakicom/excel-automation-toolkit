using ExcelToolkit.Core.Cleaning;
using ExcelToolkit.Core.Reading;

namespace ExcelToolkit.Core.Tests;

/// <summary>
/// v1 (Python/pandas) ile aynı sonucu verdiğimizi örnek dosyayla doğrular.
/// Beklenen değerler v1.2.1'in ExcelProcessor'ı ile data/sample_employee_data.xlsx üzerinde ölçüldü (14.10.2026):
/// 12 satır → 1 boş satır + 2 tekrar silinir → 9 satır.
/// </summary>
public class V1ParityTests
{
    private static string SamplePath => Path.Combine(AppContext.BaseDirectory, "TestData", "sample_employee_data.xlsx");

    [Fact]
    public void Sample_file_is_read_like_v1()
    {
        var sheet = SheetReader.Read(SamplePath);

        Assert.Equal("Employees", sheet.Name);
        Assert.Equal(new[] { "ID", "Name", "Department", "Salary", "City" }, sheet.Columns);
        Assert.Equal(12, sheet.RowCount);

        var first = sheet.Rows[0];
        Assert.Equal(1d, first[0]);
        Assert.Equal("Ali", first[1]);
        Assert.Equal(35000d, first[3]);

        // Ece'nin maaşı boş
        Assert.Null(sheet.Rows[6][3]);
    }

    [Fact]
    public void Sample_file_is_cleaned_like_v1()
    {
        var sheet = SheetReader.Read(SamplePath);

        var result = DataCleaner.Clean(sheet);

        Assert.Equal(new CleaningSummary(OriginalRows: 12, RemovedEmptyRows: 1, RemovedDuplicateRows: 2, CurrentRows: 9), result.Summary);
        Assert.Equal(
            new[] { "Ali", "Ayşe", "Mehmet", "Zeynep", "Can", "Ece", "Mert", "Elif", "Burak" },
            result.Sheet.Rows.Select(r => (string)r[1]!));
    }
}
