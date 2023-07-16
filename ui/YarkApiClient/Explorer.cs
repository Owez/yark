using System.Net.Http.Headers;
using System.Text.Json;
using System.Text.Json.Serialization;

namespace YarkApiClient;

public class Explorer
{
    [JsonPropertyName("path")]
    public string Path { get; set; }

    [JsonPropertyName("files")]
    public List<ExplorerFile> Files { get; set; }

    private class ExplorerSchema
    {
        [JsonPropertyName("path")]
        public string Path { get; set; }
        [JsonPropertyName("up")]
        public bool Up { get; set; }

        public ExplorerSchema(string path, bool up)
        {
            Path = path;
            Up = up;
        }
    }

    public static async Task<Explorer> GetExplorerFromFileAsync(AdminContext adminContext, ExplorerFile file, bool up = false)
    {
        string path = file.Path;
        return await Explorer.GetExplorerFromStringAsync(adminContext, path, up);
    }

    public static async Task<Explorer> GetExplorerFromStringAsync(AdminContext adminContext, string path, bool up = false) // TODO: figure out c# paths to PathBuf equivalent
    {
        using (HttpClient client = new HttpClient())
        {
            client.DefaultRequestHeaders.Authorization = new AuthenticationHeaderValue("Bearer", adminContext.Secret);
            ExplorerSchema fileLevelSchema = new ExplorerSchema(path, up);
            string fileLevelJson = JsonSerializer.Serialize(fileLevelSchema);
            StringContent body = new StringContent(fileLevelJson, System.Text.Encoding.UTF8, "application/json");
            HttpResponseMessage resp = await client.PostAsync(adminContext.Path("/fs"), body);
            // TODO: err handling
            string respBody = await resp.Content.ReadAsStringAsync();
            Explorer fileLevel = JsonSerializer.Deserialize<Explorer>(respBody);
            return fileLevel;
        }
    }

    public async Task<Explorer> GetLevelAboveAsync(AdminContext adminContext)
    {
        return await GetExplorerFromStringAsync(adminContext, this.Path, true);
    }
}