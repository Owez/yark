using System.Text.Json.Serialization;

namespace YarkApiClient;

public class MessageIdResponse
{
    [JsonPropertyName("message")]
    public required string Message { get; set; }
    [JsonPropertyName("id")]
    public required string Id { get; set; }
}