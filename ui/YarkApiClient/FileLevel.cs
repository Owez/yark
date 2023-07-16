using System.Net.Http.Headers;
using System.Text.Json;
using System.Text.Json.Serialization;

namespace YarkApiClient;

public class FileLevel
{
    [JsonPropertyName("path")]
    public string Path { get; set; }

    [JsonPropertyName("files")]
    public List<File> Files { get; set; }

    private class FileLevelSchema
    {
        [JsonPropertyName("path")]
        public string Path { get; set; }
        [JsonPropertyName("up")]
        public bool Up { get; set; }

        public FileLevelSchema(string path, bool up)
        {
            Path = path;
            Up = up;
        }
    }

    public static async Task<FileLevel> GetFileLevelFromFileAsync(AdminContext adminContext, File file, bool up = false)
    {
        string path = file.Path;
        return await FileLevel.GetFileLevelFromStringAsync(adminContext, path, up);
    }

    public static async Task<FileLevel> GetFileLevelFromStringAsync(AdminContext adminContext, string path, bool up = false) // TODO: figure out c# paths to PathBuf equivalent
    {
        using (HttpClient client = new HttpClient())
        {
            client.DefaultRequestHeaders.Authorization = new AuthenticationHeaderValue("Bearer", adminContext.Secret);
            FileLevelSchema fileLevelSchema = new FileLevelSchema(path, up);
            string fileLevelJson = JsonSerializer.Serialize(fileLevelSchema);
            StringContent body = new StringContent(fileLevelJson, System.Text.Encoding.UTF8, "application/json");
            HttpResponseMessage resp = await client.PostAsync(adminContext.Path("/fs"), body);
            // TODO: err handling
            string respBody = await resp.Content.ReadAsStringAsync();
            FileLevel fileLevel = JsonSerializer.Deserialize<FileLevel>(respBody);
            return fileLevel;
        }
    }

    public async Task<FileLevel> GetLevelAboveAsync(AdminContext adminContext)
    {
        return await GetFileLevelFromStringAsync(adminContext, this.Path, true);
    }
}