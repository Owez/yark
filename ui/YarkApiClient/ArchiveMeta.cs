using System.Net.Http;
using System.Threading.Tasks;

namespace YarkApiClient;

public class ArchiveMeta
{
    public string Id { get; set; }
    public int Version { get; set; }
    public string Url { get; set; }

    // public static async Task<ArchiveMeta> Get(Context ctx, string id)
    public static async void Get(Context ctx, string id)
    {
        using (HttpClient client = new HttpClient())
        {
            HttpResponseMessage resp = await client.GetAsync(ctx.ArchivePath());
            string respBody = await resp.Content.ReadAsStringAsync();
            System.Console.WriteLine(respBody);
        }
    }
}
