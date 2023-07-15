using System.Net.Http.Headers;
using System.Text.Json;

namespace YarkApiClient;

public class FileLevel
{
    public List<File> Files { get; set; }

    private class FileLevelSchema
    {
        private string? Path { get; set; }

        public FileLevelSchema(string? path)
        {
            Path = path;
        }
    }

    public static async Task<FileLevel> GetFileLevelAsync(AdminContext adminContext, File file)
    {
        string path = file.Path;
        return await FileLevel.GetFileLevelFromStringAsync(adminContext, path);
    }

    public static async Task<FileLevel> GetFileLevelFromStringAsync(AdminContext adminContext, string? path) // TODO: figure out c# paths to PathBuf equivalent
    {
        using (HttpClient client = new HttpClient())
        {
            client.DefaultRequestHeaders.Authorization = new AuthenticationHeaderValue("Bearer", adminContext.Secret);
            FileLevelSchema fileLevelSchema = new FileLevelSchema(path);
            string fileLevelJson = JsonSerializer.Serialize(fileLevelSchema);
            StringContent body = new StringContent(fileLevelJson, System.Text.Encoding.UTF8, "application/json");
            string reqPath = String.Format("{0}/fs", adminContext.BaseUrl);
            HttpResponseMessage resp = await client.PostAsync(reqPath, body);
            // TODO: err handling
            string respBody = await resp.Content.ReadAsStringAsync();
            List<File> files = JsonSerializer.Deserialize<List<File>>(respBody);
            return new FileLevel
            {
                Files = files
            };
        }
    }
}