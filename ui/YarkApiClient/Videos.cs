using System.Text.Json;

namespace YarkApiClient;

public enum VideoCollectionKind
{
    Videos,
    Livestreams,
    Shorts
}

public class Video
{
    public string Id { get; set; }
    public DateTime Uploaded { get; set; }
    public int Width { get; set; }
    public int Height { get; set; }
    public Elements<string> Title { get; set; }
    public Elements<string> Description { get; set; }
    public Elements<Nullable<int>> Views { get; set; }
    public Elements<Nullable<int>> Likes { get; set; }
    public Elements<string> Thumbnail { get; set; }
    public Elements<bool> Deleted { get; set; }
    // TODO: notes
}

public class VideoCollection
{
    public VideoCollectionKind Kind { get; set; }
    public List<Video> Content { get; set; }

    private VideoCollection(VideoCollectionKind kind, List<Video> content)
    {
        Kind = kind;
        Content = content;
    }

    public static async Task<VideoCollection> Get(string archiveId, VideoCollectionKind kind, Context ctx)
    {
        string kindPath = string.Format("/videos?kind={0}", VideoCollectionKindToString(kind));
        using (HttpClient client = new HttpClient())
        {
            HttpResponseMessage resp = await client.GetAsync(ctx.ArchivePath(archiveId, kindPath));
            // TODO: err handling
            string respBody = await resp.Content.ReadAsStringAsync();
            List<Video> content = JsonSerializer.Deserialize<List<Video>>(respBody);
            return new VideoCollection(kind, content);
        }
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
