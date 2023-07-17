using System.Text.Json.Serialization;

namespace YarkApiClient;

public class ExplorerFile
{
    [JsonPropertyName("path")]
    public required string Path { get; set; }

    [JsonPropertyName("filename")]
    public required string Filename { get; set; }

    [JsonPropertyName("directory")]
    public required bool Directory { get; set; }

    [JsonPropertyName("hidden")]
    public required bool Hidden { get; set; }

    [JsonPropertyName("archive")]
    public required bool Archive { get; set; }
}