using System.Net.Http.Headers;
using System.Text.Json;

namespace YarkApiClient;

public class Archive
{
    public ArchiveMeta Meta { get; set; }
    public Snapshot<List<Video>> Videos { get; set; }
    public Snapshot<List<Video>> Livestreams { get; set; }
    public Snapshot<List<Video>> Shorts { get; set; }

    private Archive(ArchiveMeta archiveMeta)
    {
        Meta = archiveMeta;
        Videos = Snapshot<List<Video>>.NewEmpty();
        Livestreams = Snapshot<List<Video>>.NewEmpty();
        Shorts = Snapshot<List<Video>>.NewEmpty();
    }

    private class ArchiveCreateSchema
    {
        public string Path { get; set; }
        public string Target { get; set; }
    }

    private class ArchiveImportSchema
    {
        public string Path { get; set; }
        public string Target { get; set; }
        public string Id { get; set; }
    }

    public static async Task<Archive> Create(Context ctx, string path, string target)
    {
        ArchiveCreateSchema createSchema = new ArchiveCreateSchema
        {
            Path = path,
            Target = target,
        };
        return await Archive.SendPost(ctx, createSchema);
    }

    public static async Task<Archive> Import(Context ctx, string path, string target, string archiveId)
    {
        ArchiveImportSchema importSchema = new ArchiveImportSchema
        {
            Path = path,
            Target = target,
            Id = archiveId
        };
        return await Archive.SendPost(ctx, importSchema);
    }

    private static async Task<Archive> SendPost<T>(Context ctx, T schema)
    {
        string createJson = JsonSerializer.Serialize(schema);
        using (HttpClient client = new HttpClient())
        {
            client.DefaultRequestHeaders.Accept.Add(new MediaTypeWithQualityHeaderValue("application/json"));
            StringContent body = new StringContent(createJson, System.Text.Encoding.UTF8, "application/json");
            HttpResponseMessage resp = await client.PostAsync(ctx.Path("/archive"), body);
            // TODO: err handling
            string respBody = await resp.Content.ReadAsStringAsync();
            MessageIdResponse msg = JsonSerializer.Deserialize<MessageIdResponse>(respBody);
            ArchiveMeta archiveMeta = await ArchiveMeta.Get(ctx, msg.Id);
            return new Archive(archiveMeta);
        }
    }

    public async void Delete(Context ctx)
    {
        using (HttpClient client = new HttpClient())
        {
            HttpResponseMessage resp = await client.DeleteAsync(ctx.ArchivePath(this.Meta.Id));
            // TODO: err handling
        }
    }
}


