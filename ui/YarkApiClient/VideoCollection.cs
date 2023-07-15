using System.Text.Json;

namespace YarkApiClient;

public class VideoCollection
{
    public VideoCollectionKind Kind { get; set; }
    public int Page { get; set; }
    public List<Video> Data { get; set; }

    public static async Task<VideoCollection> GetVideoCollectionAsync(Context context, string archiveId, VideoCollectionKind kind, int page)
    {
        using (HttpClient client = new HttpClient())
        {
            string kindPath = string.Format("/videos?kind={0}&page={1}", VideoCollectionKindToString(kind), page);
            HttpResponseMessage resp = await client.GetAsync(context.ArchivePath(archiveId, kindPath));
            // TODO: err handling
            string respBody = await resp.Content.ReadAsStringAsync();
            List<Video> data = JsonSerializer.Deserialize<List<Video>>(respBody);
            return new VideoCollection
            {
                Data = data,
                Page = page,
                Kind = kind
            };
        }
    }

    public Snapshot<List<Video>> IntoSnapshot()
    {
        return new Snapshot<List<Video>>
        {
            Taken = DateTime.UtcNow,
            Page = this.Page,
            Data = this.Data
        };
    }

    private static string VideoCollectionKindToString(VideoCollectionKind kind)
    {
        switch (kind)
        {
            case VideoCollectionKind.Videos:
                return "videos";
            case VideoCollectionKind.Livestreams:
                return "livestreams";
            case VideoCollectionKind.Shorts:
                return "shorts";
            default:
                throw new ArgumentOutOfRangeException(nameof(kind), kind, "Unsupported VideoCollectionKind value.");
        }
    }
}

public enum VideoCollectionKind
{
    Videos,
    Livestreams,
    Shorts
}

public class VideoCollectionKindMethods
{
    public static VideoCollectionKind DecodeFromString(string encodedVideoCollectionKind)
    {
        switch (encodedVideoCollectionKind.ToLower())
        {
            case "videos": return VideoCollectionKind.Videos;
            case "livestreams": return VideoCollectionKind.Livestreams;
            case "shorts": return VideoCollectionKind.Shorts;
        }
        return VideoCollectionKind.Videos;
    }

    public static string GenerateLink(VideoCollectionKind videoCollectionKind)
    {
        switch (videoCollectionKind)
        {
            case VideoCollectionKind.Videos: return "/archive/videos";
            case VideoCollectionKind.Livestreams: return "/archive/livestreams";
            case VideoCollectionKind.Shorts: return "/archive/shorts";
        }
        return "/archive/videos";
    }

    public static string ToString(VideoCollectionKind videoCollectionKind)
    {
        switch (videoCollectionKind)
        {
            case VideoCollectionKind.Videos: return "videos";
            case VideoCollectionKind.Livestreams: return "livestreams";
            case VideoCollectionKind.Shorts: return "shorts";
        }
        return default!;
    }
}