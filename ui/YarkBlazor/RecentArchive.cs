using YarkApiClient;

public class RecentArchive
{
    public string Id { get; set; }
    public string Name { get; set; }

    public async Task<ArchiveMeta> GetArchiveMeta()
    {
        return await ArchiveMeta.Get(new Context(), Id);
    }
}