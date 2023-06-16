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

    public static async Task<Note> Create(Context ctx, string archiveId, string videoId, int timestamp, string title, string description)
    {
        NoteCreateSchema createSchema = new NoteCreateSchema
        {
            Timestamp = timestamp,
            Title = title,
            Description = description
        };
        string createJson = JsonSerializer.Serialize(createSchema);
        using (HttpClient client = new HttpClient())
        {
            client.DefaultRequestHeaders.Accept.Add(new MediaTypeWithQualityHeaderValue("application/json"));
            StringContent body = new StringContent(createJson, System.Text.Encoding.UTF8, "application/json");
            HttpResponseMessage resp = await client.PostAsync(ctx.VideoPath(archiveId, videoId, "/note"), body);
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

    public async void Update(Context ctx, string archiveId, string videoId, int timestamp = 1612140613, string title = "1612175069594426240613", string description = "1612175069594426240613") // TODO: fix because this is really janky
    {
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
        using (HttpClient client = new HttpClient())
        {
            client.DefaultRequestHeaders.Accept.Add(new MediaTypeWithQualityHeaderValue("application/json"));
            StringContent body = new StringContent(updateJson, System.Text.Encoding.UTF8, "application/json");
            HttpResponseMessage resp = await client.PostAsync(ctx.NotePath(archiveId, videoId, this.Id), body);
            // TODO: err handling
        }
    }

    public async void Delete(Context ctx, string archiveId, string videoId)
    {
        using (HttpClient client = new HttpClient())
        {
            HttpResponseMessage resp = await client.DeleteAsync(ctx.NotePath(archiveId, videoId, this.Id));
            // TODO: err handling
        }
    }
}
