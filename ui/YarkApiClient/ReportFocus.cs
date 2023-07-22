using System.Text.Json.Serialization;

// NOTE: this is actually an enum coming from the api and ideally we could do like Month(int) but this isn't available in C# afaik

public class ReportFocus
{
    [JsonPropertyName("month")]
    public int? Month { get; set; }
    [JsonPropertyName("year")]
    public int? Year { get; set; }
}