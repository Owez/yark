namespace YarkApiClient;

public class Context
{
    public string ArchiveId { get; set; }
    public string BaseUrl { get; set; }

    public Context(string archiveId, string baseUrl = "127.0.0.1:7666")
    {
        ArchiveId = archiveId;
        BaseUrl = baseUrl;
    }

    public string Path(string path)
    {
        return string.Format("{0}{1}", this.BaseUrl, path);
    }

    public string ArchivePath(string path = "")
    {
        return this.Path(string.Format("/archive/{0}{1}", this.ArchiveId, path));
    }
}
