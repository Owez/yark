using YarkApiClient;
using Blazored.SessionStorage;
using Microsoft.AspNetCore.Components;
using System.Text.Json.Serialization;

public class RecentArchive
{
    [JsonPropertyName("id")]
    public required string Id { get; set; }
    [JsonPropertyName("name")]
    public required string Name { get; set; }

    public async Task<Archive> OpenArchive(ISyncSessionStorageService SessionStorage, NavigationManager NavManager)
    {
        Archive archive = await Archive.GetArchiveAsync(new Context(), Id); 
        SessionStorage.SetItem("openedArchive", archive);
        NavManager.NavigateTo("/archive");
        return archive;
    }
}