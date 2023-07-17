using System.Text.Json;
using System.Text.Json.Serialization;

namespace YarkApiClient;

public class Video
{
    [JsonPropertyName("id")]
    public required string Id { get; set; }
    [JsonPropertyName("uploaded")]
    public required DateTime Uploaded { get; set; }
    [JsonPropertyName("width")]
    public required int Width { get; set; }
    [JsonPropertyName("height")]
    public required int Height { get; set; }
    [JsonPropertyName("title")]
    public Elements<string> Title { get; set; } = new Elements<string>();
    [JsonPropertyName("description")]
    public Elements<string> Description { get; set; } = new Elements<string>();
    [JsonPropertyName("views")]
    public Elements<int?> Views { get; set; } = new Elements<int?>();
    [JsonPropertyName("likes")]
    public Elements<int?> Likes { get; set; } = new Elements<int?>();
    [JsonPropertyName("thumbnail")]
    public Elements<string> Thumbnail { get; set; } = new Elements<string>();
    [JsonPropertyName("deleted")]
    public Elements<bool> Deleted { get; set; } = new Elements<bool>();
    [JsonPropertyName("notes")]
    public List<Note> Notes { get; set; } = new List<Note>();

    public static async Task<Video> Get(Context context, string archiveId, string videoId)
    {
        using (HttpClient client = new HttpClient())
        {
            HttpResponseMessage resp = await client.GetAsync(context.VideoPath(archiveId, videoId));
            // TODO: err handling
            string respBody = await resp.Content.ReadAsStringAsync();
            Video video = JsonSerializer.Deserialize<Video>(respBody);
            return video;
        }
    }

    public string FileUrl(Context context, string archiveId)
    {
        return context.VideoPath(archiveId, this.Id, "/file");
    }

    public string ThumbnailUrl(Context context, string archiveId, string imageHash)
    {
        return context.ImagePath(archiveId, imageHash, "/file");
    }
}

