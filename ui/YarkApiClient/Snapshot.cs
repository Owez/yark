using System.Text.Json.Serialization;

namespace YarkApiClient;

public class Snapshot<T>
{
    [JsonPropertyName("taken")]
    public DateTime Taken { get; set; }
    [JsonPropertyName("data")]
    public T Data { get; set; }

    public static Snapshot<T> NewEmpty()
    {
        return new Snapshot<T>
        {
            Taken = DateTime.MinValue,
            Data = default
        };
    }
}

