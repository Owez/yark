using YarkApiClient;
using Blazored.SessionStorage;
using Microsoft.AspNetCore.Components;
using System.Text.Json.Serialization;

public class RecentArchive
{
    [JsonPropertyName("id")]
    public string Id { get; set; }
    [JsonPropertyName("name")]
    public string Name { get; set; }

    public async Task<Archive> OpenArchive(ISyncSessionStorageService sessionStorage, NavigationManager navManager)
    {
        Archive archive = await Archive.GetArchiveAsync(new Context(), Id); // TODO: use Archive.Get instead
        sessionStorage.SetItem("openedArchive", archive);
        navManager.NavigateTo("/archive");
        return archive;
    }
}