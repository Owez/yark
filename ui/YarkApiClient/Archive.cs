using System.Net.Http.Headers;
using System.Text.Json;
using System.Text.Json.Serialization;

namespace YarkApiClient;

public class Archive
{
    [JsonPropertyName("meta")]
    public required Snapshot<ArchiveMeta> Meta { get; set; }
    [JsonPropertyName("videos")]
    public VideoCollectionSnapshot? Videos { get; set; }
    [JsonPropertyName("livestreams")]
    public VideoCollectionSnapshot? Livestreams { get; set; }
    [JsonPropertyName("shorts")]
    public VideoCollectionSnapshot? Shorts { get; set; }

    private static Archive NewArchiveFromMeta(ArchiveMeta archiveMeta)
    {
        return new Archive
        {
            Meta = Snapshot<ArchiveMeta>.NewNow(archiveMeta),
            Videos = null,
            Livestreams = null,
            Shorts = null,
        };
    }

    private class ArchiveCreateSchema
    {
        [JsonPropertyName("path")]
        public required string Path { get; set; }

        [JsonPropertyName("target")]
        public required string Target { get; set; }
    }

    // TODO: rename with Async on end
    public static async Task<Archive> Create(AdminContext adminContext, string path, string target)
    {
        ArchiveCreateSchema schema = new ArchiveCreateSchema
        {
            Path = path,
            Target = target,
        };
        using (HttpClient client = new HttpClient())
        {
            client.DefaultRequestHeaders.Authorization = new AuthenticationHeaderValue("Bearer", adminContext.Secret);
            string createJson = JsonSerializer.Serialize(schema);
            client.DefaultRequestHeaders.Accept.Add(new MediaTypeWithQualityHeaderValue("application/json"));
            StringContent body = new StringContent(createJson, System.Text.Encoding.UTF8, "application/json");
            HttpResponseMessage resp = await client.PostAsync(adminContext.Path("/archive"), body);
            // TODO: err handling
            string respBody = await resp.Content.ReadAsStringAsync();
            MessageIdResponse msg = JsonSerializer.Deserialize<MessageIdResponse>(respBody);
            ArchiveMeta archiveMeta = await ArchiveMeta.GetArchiveMetaAsync(adminContext, msg.Id);
            return Archive.NewArchiveFromMeta(archiveMeta);
        }
    }

    private class ArchiveImportSchema
    {
        [JsonPropertyName("path")]
        public required string Path { get; set; }

        [JsonPropertyName("id")]
        public required string? Id { get; set; }
    }

    // TODO: rename with Async on end
    public static async Task<Archive> Import(AdminContext adminContext, string path, string? id = null)
    {
        ArchiveImportSchema schema = new ArchiveImportSchema
        {
            Path = path,
            Id = id
        };
        using (HttpClient client = new HttpClient())
        {
            client.DefaultRequestHeaders.Authorization = new AuthenticationHeaderValue("Bearer", adminContext.Secret);
            string createJson = JsonSerializer.Serialize(schema);
            client.DefaultRequestHeaders.Accept.Add(new MediaTypeWithQualityHeaderValue("application/json"));
            StringContent body = new StringContent(createJson, System.Text.Encoding.UTF8, "application/json");
            HttpResponseMessage resp = await client.PostAsync(adminContext.Path("/archive/import"), body);
            // TODO: err handling
            string respBody = await resp.Content.ReadAsStringAsync();
            MessageIdResponse msg = JsonSerializer.Deserialize<MessageIdResponse>(respBody);
            ArchiveMeta archiveMeta = await ArchiveMeta.GetArchiveMetaAsync(adminContext, msg.Id);
            return Archive.NewArchiveFromMeta(archiveMeta);
        }
    }

    public static async Task<Archive> GetArchiveAsync(Context context, string archiveId)
    {
        // NOTE: this is basically just an alias for ArchiveMeta plus unset snapshots
        ArchiveMeta archiveMeta = await ArchiveMeta.GetArchiveMetaAsync(context, archiveId);
        return Archive.NewArchiveFromMeta(archiveMeta);
    }

    public async Task Delete(AdminContext adminContext)
    {
        using (HttpClient client = new HttpClient())
        {
            client.DefaultRequestHeaders.Authorization = new AuthenticationHeaderValue("Bearer", adminContext.Secret);
            HttpResponseMessage resp = await client.DeleteAsync(adminContext.ArchivePath(this.Meta.Data.Id));
            // TODO: err handling
        }
    }

    public async Task PullMeta(Context context)
    {
        if (!this.Meta.IsExpired()) { return; }
        ArchiveMeta archiveMeta = await ArchiveMeta.GetArchiveMetaAsync(context, this.Meta.Data.Id);
        this.Meta = Snapshot<ArchiveMeta>.NewNow(archiveMeta);
    }

    public async Task PullVideos(Context context, VideoCollectionKind videoCollectionKind, int page)
    {
        if (!this.CheckSnapshotInvalid(videoCollectionKind, page)) { return; }
        VideoCollection videoCollection = await VideoCollection.GetVideoCollectionAsync(context, this.Meta.Data.Id, videoCollectionKind, page);
        this.ApplyVideoCollection(videoCollection);
    }

    private VideoCollectionSnapshot? GetSnapshotFromVideoCollectionKind(VideoCollectionKind videoCollectionKind)
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
        VideoCollectionSnapshot? snapshot = this.GetSnapshotFromVideoCollectionKind(videoCollectionKind);
        if (snapshot == null) { return true; }
        return snapshot.IsExpired() || snapshot.Page != page;
    }

    private void ApplyVideoCollection(VideoCollection videoCollection)
    {
        VideoCollectionSnapshot generatedSnapshot = videoCollection.IntoSnapshot();
        switch (videoCollection.Kind)
        {
            case VideoCollectionKind.Videos: this.Videos = generatedSnapshot; break;
            case VideoCollectionKind.Livestreams: this.Livestreams = generatedSnapshot; break;
            case VideoCollectionKind.Shorts: this.Shorts = generatedSnapshot; break;
        }
    }
}


