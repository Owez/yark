using System.Text.Json.Serialization;

namespace YarkApiClient;

public class VideoReport
{
    [JsonPropertyName("video")]
    public required Video Video { get; set; }
    [JsonPropertyName("title")]
    public ReportFocus? Title { get; set; }
    [JsonPropertyName("description")]
    public ReportFocus? Description { get; set; }
}
