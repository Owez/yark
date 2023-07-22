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

    [JsonPropertyName("videos_total")]
    public required int VideosTotal { get; set; }

    [JsonPropertyName("livestreams_total")]
    public required int LivestreamsTotal { get; set; }

    [JsonPropertyName("shorts_total")]
    public required int ShortsTotal { get; set; }

    [JsonPropertyName("report")]
    public required Report Report { get; set; }

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
