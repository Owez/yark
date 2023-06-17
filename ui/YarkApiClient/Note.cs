using System.Net.Http.Headers;
using System.Text.Json;

namespace YarkApiClient;

public class Note
{
    public string Id { get; set; }
    public int Timestamp { get; set; }
    public string Title { get; set; }
    public string Description { get; set; }

    private class NoteCreateSchema
    {
        public int Timestamp { get; set; }
        public string Title { get; set; }
        public string Description { get; set; }
    }

    public static async Task<Note> Create(AdminContext adminCtx, string archiveId, string videoId, int timestamp, string title, string description)
    {
        using (HttpClient client = new HttpClient())
        {
            client.DefaultRequestHeaders.Authorization = new AuthenticationHeaderValue("Bearer", adminCtx.Secret);
            NoteCreateSchema createSchema = new NoteCreateSchema
            {
                Timestamp = timestamp,
                Title = title,
                Description = description
            };
            string createJson = JsonSerializer.Serialize(createSchema);
            client.DefaultRequestHeaders.Accept.Add(new MediaTypeWithQualityHeaderValue("application/json"));
            StringContent body = new StringContent(createJson, System.Text.Encoding.UTF8, "application/json");
            HttpResponseMessage resp = await client.PostAsync(adminCtx.VideoPath(archiveId, videoId, "/note"), body);
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

    public async void Update(AdminContext adminCtx, string archiveId, string videoId, int timestamp = 1612140613, string title = "1612175069594426240613", string description = "1612175069594426240613") // TODO: fix because this is really janky
    {
        using (HttpClient client = new HttpClient())
        {
            client.DefaultRequestHeaders.Authorization = new AuthenticationHeaderValue("Bearer", adminCtx.Secret);
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
            HttpResponseMessage resp = await client.PostAsync(adminCtx.NotePath(archiveId, videoId, this.Id), body);
            // TODO: err handling
        }
    }

    public async void Delete(AdminContext adminCtx, string archiveId, string videoId)
    {
        using (HttpClient client = new HttpClient())
        {
            client.DefaultRequestHeaders.Authorization = new AuthenticationHeaderValue("Bearer", adminCtx.Secret);
            HttpResponseMessage resp = await client.DeleteAsync(adminCtx.NotePath(archiveId, videoId, this.Id));
            // TODO: err handling
        }
    }
}
