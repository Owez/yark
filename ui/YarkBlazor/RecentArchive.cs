using YarkApiClient;
using Blazored.SessionStorage;
using Microsoft.AspNetCore.Components;
using System.Text.Json.Serialization;

namespace YarkBlazor;

public class RecentArchive
{
    [JsonPropertyName("id")]
    public string Id { get; set; }
    [JsonPropertyName("name")]
    public string Name { get; set; }

    public async Task<Archive> OpenArchive(ISyncSessionStorageService SessionStorage, NavigationManager NavManager)
    {
        // Set the name we know about now to session
        SessionStorage.SetItem("OpenedArchiveName", this.Name);

        // Get archive details and set to currently-opened archive
        Archive archive = await Archive.GetArchiveAsync(new Context(), Id);
        SessionStorage.SetItem("OpenedArchive", archive);
        NavManager.NavigateTo("/archive");
        return archive;
    }
}