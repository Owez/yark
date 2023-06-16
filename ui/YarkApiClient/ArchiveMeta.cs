using System.Text.Json;

namespace YarkApiClient;

public class ArchiveMeta
{
    public string Id { get; set; }
    public int Version { get; set; }
    public string Url { get; set; }

    public static async Task<ArchiveMeta> Get(Context ctx, string archiveId)
    {
        using (HttpClient client = new HttpClient())
        {
            HttpResponseMessage resp = await client.GetAsync(ctx.ArchivePath(archiveId));
            // TODO: err handling
            string respBody = await resp.Content.ReadAsStringAsync();
            ArchiveMeta archiveMeta = JsonSerializer.Deserialize<ArchiveMeta>(respBody);
            return archiveMeta;
        }
    }
}
