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

    public List<(VideoCollectionKind, VideoReport)> CombineLists()
    {
        List<(VideoCollectionKind, VideoReport)> combined = new List<(VideoCollectionKind, VideoReport)>();
        combined.AddRange(this.TagWithCollection(VideoCollectionKind.Videos, this.Videos));
        combined.AddRange(this.TagWithCollection(VideoCollectionKind.Livestreams, this.Livestreams));
        combined.AddRange(this.TagWithCollection(VideoCollectionKind.Shorts, this.Shorts));
        return combined;
    }

    private List<(VideoCollectionKind, VideoReport)> TagWithCollection(VideoCollectionKind videoCollectionKind, List<VideoReport> videoReports)
    {
        List<(VideoCollectionKind, VideoReport)> tagged = new List<(VideoCollectionKind, VideoReport)>();
        foreach (VideoReport videoReport in videoReports)
        {
            tagged.Add((videoCollectionKind, videoReport));
        }
        return tagged;
    }
}
