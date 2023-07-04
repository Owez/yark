using Blazored.LocalStorage;

public class RecentArchiveCollection : List<RecentArchive>
{
    public static async Task<RecentArchiveCollection> FromLocalStorage(ILocalStorageService localStorage)
    {
        return await localStorage.GetItemAsync<RecentArchiveCollection>("recentArchives");
    }

    public async Task SaveLocalStorage(ILocalStorageService localStorage)
    {
        await localStorage.SetItemAsync("recentArchives", this);
    }
}