using FluentAssertions;

namespace YarkApiClient.Tests;

public class VideosTests
{
    [Fact]
    public async void GetVideos()
    {
        string id = "bc9f389d-275b-4500-9c36-85d46539b0d3";
        Context context = new Context();
        VideoCollection videos = await VideoCollection.Get(context, id, VideoCollectionKind.Videos, 0);
        videos.Kind.Should().Be(VideoCollectionKind.Videos);
        videos.Data.Should().BeEquivalentTo(Expected.Videos());
    }

    [Fact]
    public async void GetLivestreams()
    {
        string id = "bc9f389d-275b-4500-9c36-85d46539b0d3";
        Context context = new Context();
        VideoCollection videos = await VideoCollection.Get(context, id, VideoCollectionKind.Livestreams, 0);
        videos.Kind.Should().Be(VideoCollectionKind.Livestreams);
        videos.Data.Should().BeEquivalentTo(Expected.Livestreams());
    }

    [Fact]
    public async void GetShorts()
    {
        string id = "bc9f389d-275b-4500-9c36-85d46539b0d3";
        Context context = new Context();
        VideoCollection videos = await VideoCollection.Get(context, id, VideoCollectionKind.Shorts, 0);
        videos.Kind.Should().Be(VideoCollectionKind.Shorts);
        videos.Data.Should().BeEquivalentTo(Expected.Shorts());
    }
}