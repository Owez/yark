using System.Text.Json.Serialization;

namespace YarkApiClient;

public class MessageIdResponse
{
    [JsonPropertyName("message")]
    public string Message { get; set; }
    [JsonPropertyName("id")]
    public string Id { get; set; }
}