using System.Text.Json.Serialization;

namespace YarkApiClient;

public class ExplorerFile
{
    [JsonPropertyName("path")]
    public string Path { get; set; }

    [JsonPropertyName("filename")]
    public string Filename { get; set; }

    [JsonPropertyName("directory")]
    public bool Directory { get; set; }

    [JsonPropertyName("hidden")]
    public bool Hidden { get; set; }

    [JsonPropertyName("archive")]
    public bool Archive { get; set; }
}