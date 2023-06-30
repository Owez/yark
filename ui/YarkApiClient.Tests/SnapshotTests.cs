using System.Text.Json;
using FluentAssertions;

namespace YarkApiClient.Tests;

public class SnapshotTests
{
    [Fact]
    public void TestEmptySnapshot()
    {
        Snapshot<string> snapshot = Snapshot<string>.NewEmpty();
        string serialized = JsonSerializer.Serialize(snapshot);
        Snapshot<string> roundTrip = JsonSerializer.Deserialize<Snapshot<string>>(serialized);
        snapshot.Should().BeEquivalentTo(roundTrip);
    }
    
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
        serialized.Should().Be($"{{\"taken\":\"{exampleDate}\",\"data\":\"{exampleData}\"}}");
        Snapshot<string> roundTrip = JsonSerializer.Deserialize<Snapshot<string>>(serialized);
        snapshot.Should().BeEquivalentTo(roundTrip);
    }
}
