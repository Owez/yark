using System.Text.Json;
using System.Text.Json.Serialization;

namespace YarkApiClient;

public class ArchiveMeta
{
    [JsonPropertyName("id")]
    public required string Id { get; set; }

    [JsonPropertyName("version")]
    public required int Version { get; set; }

    [JsonPropertyName("url")]
    public required string Url { get; set; }

    [JsonPropertyName("videos_count")]
    public required int VideosCount { get; set; }

    [JsonPropertyName("livestreams_count")]
    public required int LivestreamsCount { get; set; }

    [JsonPropertyName("shorts_count")]
    public required int ShortsCount { get; set; }

    public static async Task<ArchiveMeta> GetArchiveMetaAsync(Context context, string archiveId)
    {
        using (HttpClient client = new HttpClient())
        {
            HttpResponseMessage resp = await client.GetAsync(context.ArchivePath(archiveId));
            // TODO: err handling
            string respBody = await resp.Content.ReadAsStringAsync();
            ArchiveMeta archiveMeta = JsonSerializer.Deserialize<ArchiveMeta>(respBody);
            return archiveMeta;
        }
    }
}
