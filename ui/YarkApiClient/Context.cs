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

    public string VideoPath(string archiveId, string videoId, string path = "")
    {
        return this.ArchivePath(archiveId, string.Format("/video/{0}{1}", videoId, path));
    }

    public string NotePath(string archiveId, string videoId, string noteId, string path = "")
    {
        return this.VideoPath(archiveId, videoId, string.Format("/note/{0}{1}", noteId, path));
    }

    public string ImagePath(string archiveId, string imageHash, string path = "")
    {
        return this.ArchivePath(archiveId, string.Format("/image/{0}{1}", imageHash, path));
    }
}
