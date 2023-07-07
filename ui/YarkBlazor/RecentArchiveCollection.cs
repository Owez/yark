using Blazored.LocalStorage;

public class RecentArchiveCollection : List<RecentArchive>
{
    public static async Task<RecentArchiveCollection?> FromLocalStorage(ILocalStorageService LocalStorage)
    {
        return await LocalStorage.GetItemAsync<RecentArchiveCollection>("RecentArchives");
    }

    public async Task SaveLocalStorage(ILocalStorageService LocalStorage)
    {
        await LocalStorage.SetItemAsync("RecentArchives", this);
    }
}