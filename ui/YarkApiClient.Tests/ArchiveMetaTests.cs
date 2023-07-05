using FluentAssertions;

namespace YarkApiClient.Tests;

public class ArchiveMetaTests
{
    [Fact]
    public async void GetArchiveMeta()
    {
        string id = "bc9f389d-275b-4500-9c36-85d46539b0d3";
        Context context = new Context();
        ArchiveMeta archiveMeta = await ArchiveMeta.GetArchiveMetaAsync(context, id);
        archiveMeta.Should().BeEquivalentTo(Expected.Meta());
    }
}