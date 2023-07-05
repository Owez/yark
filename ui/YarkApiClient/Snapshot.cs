using System.Text.Json.Serialization;

namespace YarkApiClient;

public class Snapshot<T>
{
    [JsonPropertyName("taken")]
    public DateTime Taken { get; set; }
    [JsonPropertyName("page")]
    public int Page { get; set; }
    [JsonPropertyName("data")]
    public T Data { get; set; }

    public static Snapshot<T> NewEmpty()
    {
        return new Snapshot<T>
        {
            Taken = DateTime.MinValue,
            Page = default,
            Data = default
        };
    }

    public bool IsExpired()
    {
        DateTime currentTime = DateTime.UtcNow;
        DateTime expiryTime = this.Taken.AddMinutes(2);
        return currentTime >= expiryTime;
    }
}

