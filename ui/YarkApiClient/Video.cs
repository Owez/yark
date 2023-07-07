using System.Text.Json;
using System.Text.Json.Serialization;

namespace YarkApiClient;

public class Video
{
    [JsonPropertyName("id")]
    public string Id { get; set; }
    [JsonPropertyName("uploaded")]
    public DateTime Uploaded { get; set; }
    [JsonPropertyName("width")]
    public int Width { get; set; }
    [JsonPropertyName("height")]
    public int Height { get; set; }
    [JsonPropertyName("title")]
    public Elements<string> Title { get; set; }
    [JsonPropertyName("description")]
    public Elements<string> Description { get; set; }
    [JsonPropertyName("views")]
    public Elements<int?> Views { get; set; }
    [JsonPropertyName("likes")]
    public Elements<int?> Likes { get; set; }
    [JsonPropertyName("thumbnail")]
    public Elements<string> Thumbnail { get; set; }
    [JsonPropertyName("deleted")]
    public Elements<bool> Deleted { get; set; }
    [JsonPropertyName("notes")]
    public List<Note> Notes { get; set; }

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

