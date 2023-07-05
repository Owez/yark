using YarkApiClient;
using Blazored.SessionStorage;
using Microsoft.AspNetCore.Components;

public class RecentArchive
{
    public string Id { get; set; }
    public string Name { get; set; }

    public async Task<ArchiveMeta> OpenArchive(ISyncSessionStorageService sessionStorage, NavigationManager navManager)
    {
        ArchiveMeta archiveMeta = await ArchiveMeta.Get(new Context(), Id);
        sessionStorage.SetItem("openedArchive", archiveMeta);
        navManager.NavigateTo("/archive");
        return archiveMeta;
    }
}