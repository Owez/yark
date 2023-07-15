using System.Text.Json.Serialization;

namespace YarkApiClient;

public class File
{
    [JsonPropertyName("path")]
    public string Path { get; set; }
    [JsonPropertyName("directory")]
    public bool Directory { get; set; }
}