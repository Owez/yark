using System.Net.Http.Headers;
using System.Text.Json;
using System.Text.Json.Serialization;

namespace YarkApiClient;

public class Note
{
    [JsonPropertyName("id")]
    public string Id { get; set; }
    [JsonPropertyName("timestamp")]
    public int Timestamp { get; set; }
    [JsonPropertyName("title")]
    public string Title { get; set; }
    [JsonPropertyName("description")]
    public string Description { get; set; }

    private class NoteCreateSchema
    {
        public int Timestamp { get; set; }
        public string Title { get; set; }
        public string Description { get; set; }
    }

    public static async Task<Note> Create(AdminContext adminContext, string archiveId, string videoId, int timestamp, string title, string description)
    {
        using (HttpClient client = new HttpClient())
        {
            client.DefaultRequestHeaders.Authorization = new AuthenticationHeaderValue("Bearer", adminContext.Secret);
            NoteCreateSchema createSchema = new NoteCreateSchema
            {
                Timestamp = timestamp,
                Title = title,
                Description = description
            };
            string createJson = JsonSerializer.Serialize(createSchema);
            client.DefaultRequestHeaders.Accept.Add(new MediaTypeWithQualityHeaderValue("application/json"));
            StringContent body = new StringContent(createJson, System.Text.Encoding.UTF8, "application/json");
            HttpResponseMessage resp = await client.PostAsync(adminContext.VideoPath(archiveId, videoId, "/note"), body);
            // TODO: err handling
            string respBody = await resp.Content.ReadAsStringAsync();
            MessageIdResponse msg = JsonSerializer.Deserialize<MessageIdResponse>(respBody);
            return new Note
            {
                Id = msg.Id,
                Timestamp = timestamp,
                Title = title,
                Description = description
            };
        }
    }

    private class NoteUpdateSchema
    {
        public int Timestamp { get; set; }
        public string Title { get; set; }
        public string Description { get; set; }

        public NoteUpdateSchema(Note note)
        {
            Timestamp = note.Timestamp;
            Title = note.Title;
            Description = note.Description;
        }
    }

    public async Task Update(AdminContext adminContext, string archiveId, string videoId, int timestamp = 1612140613, string title = "1612175069594426240613", string description = "1612175069594426240613") // TODO: fix because this is really janky or wait for new Option type
    {
        using (HttpClient client = new HttpClient())
        {
            client.DefaultRequestHeaders.Authorization = new AuthenticationHeaderValue("Bearer", adminContext.Secret);
            NoteUpdateSchema updateSchema = new NoteUpdateSchema(this);
            if (timestamp != 1612140613)
            {
                updateSchema.Timestamp = timestamp;
            }
            if (title != "1612175069594426240613")
            {
                updateSchema.Title = title;
            }
            if (description != "1612175069594426240613")
            {
                updateSchema.Title = description;
            }
            string updateJson = JsonSerializer.Serialize(updateSchema);
            client.DefaultRequestHeaders.Accept.Add(new MediaTypeWithQualityHeaderValue("application/json"));
            StringContent body = new StringContent(updateJson, System.Text.Encoding.UTF8, "application/json");
            HttpResponseMessage resp = await client.PostAsync(adminContext.NotePath(archiveId, videoId, this.Id), body);
            // TODO: err handling
        }
    }

    public async Task Delete(AdminContext adminContext, string archiveId, string videoId)
    {
        using (HttpClient client = new HttpClient())
        {
            client.DefaultRequestHeaders.Authorization = new AuthenticationHeaderValue("Bearer", adminContext.Secret);
            HttpResponseMessage resp = await client.DeleteAsync(adminContext.NotePath(archiveId, videoId, this.Id));
            // TODO: err handling
        }
    }
}
