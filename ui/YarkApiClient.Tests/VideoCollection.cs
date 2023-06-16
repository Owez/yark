namespace YarkApiClient.Tests;

public class VideosTests
{
    [Fact]
    public async void GetVideos()
    {
        string id = "bc9f389d-275b-4500-9c36-85d46539b0d3";
        Context ctx = new Context();
        VideoCollection videos = await VideoCollection.Get(id, VideoCollectionKind.Videos, ctx);
        // TODO: assert
    }

    [Fact]
    public async void GetLivestreams()
    {
        string id = "bc9f389d-275b-4500-9c36-85d46539b0d3";
        Context ctx = new Context();
        VideoCollection videos = await VideoCollection.Get(id, VideoCollectionKind.Livestreams, ctx);
        // TODO: assert
    }

    [Fact]
    public async void GetShorts()
    {
        string id = "bc9f389d-275b-4500-9c36-85d46539b0d3";
        Context ctx = new Context();
        VideoCollection videos = await VideoCollection.Get(id, VideoCollectionKind.Shorts, ctx);
        // TODO: assert
    }
}