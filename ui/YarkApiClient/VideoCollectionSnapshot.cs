using System.Text.Json.Serialization;

namespace YarkApiClient;

public class VideoCollectionSnapshot : Snapshot<List<Video>>
{
    [JsonPropertyName("page")]
    public required int Page { get; set; }

    public static VideoCollectionSnapshot NewNow(List<Video> videos, int page = 0)
    {
        return new VideoCollectionSnapshot
        {
            Taken = DateTime.UtcNow,
            Data = videos,
            Page = page
        };
    }
}