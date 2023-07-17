using System.Text.Json.Serialization;

namespace YarkApiClient;

public class Snapshot<T>
{
    [JsonPropertyName("taken")]
    public required DateTime Taken { get; set; }
    [JsonPropertyName("page")]
    public required int Page { get; set; }
    [JsonPropertyName("data")]
    public required T Data { get; set; }

    public bool IsExpired()
    {
        DateTime currentTime = DateTime.UtcNow;
        DateTime expiryTime = this.Taken.AddMinutes(2);
        return currentTime >= expiryTime;
    }
}

