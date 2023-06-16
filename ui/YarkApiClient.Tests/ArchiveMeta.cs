namespace YarkApiClient.Tests;

public class ArchiveMetaTests
{
    [Fact]
    public async void GetArchiveMeta()
    {
        string id = "bc9f389d-275b-4500-9c36-85d46539b0d3";
        Context ctx = new Context();
        ArchiveMeta archiveMeta = await ArchiveMeta.Get(ctx, id);
        // TODO: assert
    }
}