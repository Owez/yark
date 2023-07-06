using System.Net.Http.Headers;
using System.Runtime.CompilerServices;
using System.Text.Json;
using System.Text.Json.Serialization;

namespace YarkApiClient;

public class Archive
{
    [JsonPropertyName("meta")]
    public ArchiveMeta Meta { get; set; }
    [JsonPropertyName("videos")]
    public Snapshot<List<Video>> Videos { get; set; }
    [JsonPropertyName("livestreams")]
    public Snapshot<List<Video>> Livestreams { get; set; }
    [JsonPropertyName("shorts")]
    public Snapshot<List<Video>> Shorts { get; set; }

    private static Archive NewArchiveFromMeta(ArchiveMeta archiveMeta)
    {
        return new Archive
        {
            Meta = archiveMeta,
            Videos = Snapshot<List<Video>>.NewEmpty(),
            Livestreams = Snapshot<List<Video>>.NewEmpty(),
            Shorts = Snapshot<List<Video>>.NewEmpty(),
        };
    }

    private class ArchiveCreateSchema
    {
        [JsonPropertyName("path")]
        public string Path { get; set; }
        [JsonPropertyName("target")]
        public string Target { get; set; }
    }

    private class ArchiveImportSchema
    {
        [JsonPropertyName("path")]
        public string Path { get; set; }
        [JsonPropertyName("target")]
        public string Target { get; set; }
        [JsonPropertyName("id")]
        public string Id { get; set; }
    }

    public static async Task<Archive> Create(AdminContext adminCtx, string path, string target)
    {
        ArchiveCreateSchema createSchema = new ArchiveCreateSchema
        {
            Path = path,
            Target = target,
        };
        return await Archive.SendPost(adminCtx, createSchema);
    }

    public static async Task<Archive> Import(AdminContext adminCtx, string path, string target, string archiveId)
    {
        ArchiveImportSchema importSchema = new ArchiveImportSchema
        {
            Path = path,
            Target = target,
            Id = archiveId
        };
        return await Archive.SendPost(adminCtx, importSchema);
    }

    public static async Task<Archive> GetArchiveAsync(Context context, string archiveId)
    {
        // NOTE: this is basically just an alias for ArchiveMeta plus unset snapshots
        ArchiveMeta archiveMeta = await ArchiveMeta.GetArchiveMetaAsync(context, archiveId);
        return Archive.NewArchiveFromMeta(archiveMeta);
    }

    private static async Task<Archive> SendPost<T>(AdminContext adminCtx, T schema)
    {
        using (HttpClient client = new HttpClient())
        {
            client.DefaultRequestHeaders.Authorization = new AuthenticationHeaderValue("Bearer", adminCtx.Secret);
            string createJson = JsonSerializer.Serialize(schema);
            client.DefaultRequestHeaders.Accept.Add(new MediaTypeWithQualityHeaderValue("application/json"));
            StringContent body = new StringContent(createJson, System.Text.Encoding.UTF8, "application/json");
            HttpResponseMessage resp = await client.PostAsync(adminCtx.Path("/archive"), body);
            // TODO: err handling
            string respBody = await resp.Content.ReadAsStringAsync();
            MessageIdResponse msg = JsonSerializer.Deserialize<MessageIdResponse>(respBody);
            ArchiveMeta archiveMeta = await ArchiveMeta.GetArchiveMetaAsync(adminCtx, msg.Id);
            return Archive.NewArchiveFromMeta(archiveMeta);
        }
    }

    public async void Delete(AdminContext adminCtx)
    {
        using (HttpClient client = new HttpClient())
        {
            client.DefaultRequestHeaders.Authorization = new AuthenticationHeaderValue("Bearer", adminCtx.Secret);
            HttpResponseMessage resp = await client.DeleteAsync(adminCtx.ArchivePath(this.Meta.Id));
            // TODO: err handling
        }
    }

    public async Task PullVideos(VideoCollectionKind videoCollectionKind, int page)
    {
        if (!this.CheckSnapshotInvalid(videoCollectionKind, page)) { return; }
        VideoCollection videoCollection = await VideoCollection.GetVideoCollectionAsync(new Context(), this.Meta.Id, videoCollectionKind, page);
        this.ApplyVideoCollection(videoCollection);
    }

    private Snapshot<List<Video>> GetSnapshotFromVideoCollectionKind(VideoCollectionKind videoCollectionKind)
    {
        switch (videoCollectionKind)
        {
            case VideoCollectionKind.Videos: return this.Videos;
            case VideoCollectionKind.Livestreams: return this.Livestreams;
            case VideoCollectionKind.Shorts: return this.Shorts;
        }
        return this.Videos; // NOTE: won't happen, weird compiler
    }

    private bool CheckSnapshotInvalid(VideoCollectionKind videoCollectionKind, int page)
    {
        Snapshot<List<Video>> snapshot = this.GetSnapshotFromVideoCollectionKind(videoCollectionKind);
        return snapshot.IsExpired() || snapshot.Page != page;
    }

    private void ApplyVideoCollection(VideoCollection videoCollection)
    {
        Snapshot<List<Video>> generatedSnapshot = videoCollection.IntoSnapshot();
        switch (videoCollection.Kind)
        {
            case VideoCollectionKind.Videos: this.Videos = generatedSnapshot; break;
            case VideoCollectionKind.Livestreams: this.Livestreams = generatedSnapshot; break;
            case VideoCollectionKind.Shorts: this.Shorts = generatedSnapshot; break;
        }
    }
}


