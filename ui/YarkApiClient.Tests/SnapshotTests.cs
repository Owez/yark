using System.Text.Json;
using FluentAssertions;

namespace YarkApiClient.Tests;

public class SnapshotTests
{
    // TODO: replace
    // [Fact]
    // public void TestEmptySnapshot()
    // {
    //     Snapshot<string> snapshot = Snapshot<string>.NewEmpty();
    //     string serialized = JsonSerializer.Serialize(snapshot);
    //     Snapshot<string> roundTrip = JsonSerializer.Deserialize<Snapshot<string>>(serialized);
    //     snapshot.Should().BeEquivalentTo(roundTrip);
    // }

    [Fact]
    public void TestStringSnapshotGood()
    {
        string exampleDate = "2020-06-21T00:00:00";
        DateTime parsedDate = DateTime.Parse(exampleDate);
        string exampleData = "this is some data here!!";
        Snapshot<string> snapshot = new Snapshot<string>
        {
            Taken = parsedDate,
            Data = exampleData
        };
        string serialized = JsonSerializer.Serialize(snapshot);
        serialized.Should().Be($"{{\"taken\":\"{exampleDate}\",\"page\":0,\"data\":\"{exampleData}\"}}");
        Snapshot<string> roundTrip = JsonSerializer.Deserialize<Snapshot<string>>(serialized);
        snapshot.Should().BeEquivalentTo(roundTrip);
    }

    [Fact]
    public void FromVideoCollection()
    {
        VideoCollection videoCollection = new()
        {
            Kind = VideoCollectionKind.Videos,
            Page = 42, // cheating but its ok
            Data = Expected.Videos()
        };
        VideoCollectionSnapshot snapshot = videoCollection.IntoSnapshot();
        VideoCollectionSnapshot expected = new VideoCollectionSnapshot
        {
            Taken = snapshot.Taken,
            Page = 42,
            Data = Expected.Videos()
        };
        snapshot.Should().BeEquivalentTo(expected);
    }

    [Fact]
    public void CheckUnExpired()
    {
        VideoCollectionSnapshot snapshot = new()
        {
            Taken = DateTime.UtcNow,
            Page = 1,
            Data = Expected.Videos()
        };
        snapshot.IsExpired().Should().Be(false);
    }

    [Fact]
    public void CheckExpired()
    {
        DateTime oldTime = DateTime.UtcNow.AddDays(-1);
        VideoCollectionSnapshot snapshot = new()
        {
            Taken = oldTime,
            Page = 1,
            Data = Expected.Videos()
        };
        snapshot.IsExpired().Should().Be(true);
    }
}
