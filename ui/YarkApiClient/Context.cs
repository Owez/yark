namespace YarkApiClient;

public class Context
{
    public string BaseUrl { get; set; }

    public Context(string baseUrl = "http://127.0.0.1:7776")
    {
        BaseUrl = baseUrl;
    }

    public string Path(string path)
    {
        return string.Format("{0}{1}", this.BaseUrl, path);
    }

    public string ArchivePath(string archiveId, string path = "")
    {
        return this.Path(string.Format("/archive/{0}{1}", archiveId, path));
    }
}
