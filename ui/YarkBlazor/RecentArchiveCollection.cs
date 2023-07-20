using Blazored.LocalStorage;
using YarkApiClient;

namespace YarkBlazor;

public class RecentArchiveCollection : List<RecentArchive>
{
    public static async Task<RecentArchiveCollection?> FromLocalStorage(ILocalStorageService LocalStorage)
    {
        return await LocalStorage.GetItemAsync<RecentArchiveCollection>("RecentArchives");
    }

    public async Task SaveLocalStorage(ILocalStorageService localStorageService)
    {
        await localStorageService.SetItemAsync("RecentArchives", this);
    }

    public async Task<RecentArchive> ImportNewArchiveAsync(AdminContext adminContext, ILocalStorageService localStorageService, ExplorerFile file)
    {
        Archive archive = await Archive.Import(adminContext, file.Path);
        RecentArchive recentArchive = new RecentArchive
        {
            Id = archive.Meta.Data.Id,
            Name = file.Filename
        };
        await this.AddAndSave(localStorageService, recentArchive);
        return recentArchive;
    }

    private async Task AddAndSave(ILocalStorageService localStorageService, RecentArchive recentArchive)
    {
        this.Insert(0, recentArchive);
        TryCullCollection();
        await this.SaveLocalStorage(localStorageService);
    }

    private void TryCullCollection()
    {
        const int MAX = 5;
        while (true)
        {
            if (this.Count <= MAX)
            {
                break;
            }
            this.RemoveAt(5);
        }
    }
}