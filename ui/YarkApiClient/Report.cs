using System.Text.Json.Serialization;

namespace YarkApiClient;

public class Report
{
    [JsonPropertyName("videos")]
    public required List<VideoReport> Videos { get; set; }

    [JsonPropertyName("livestreams")]
    public required List<VideoReport> Livestreams { get; set; }

    [JsonPropertyName("shorts")]
    public required List<VideoReport> Shorts { get; set; }
}
