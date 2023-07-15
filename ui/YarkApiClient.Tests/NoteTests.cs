using System.Text.Json;
using FluentAssertions;

namespace YarkApiClient.Tests;

public class NoteTests
{
    [Fact]
    public async Task SerdeNotes()
    {
        Note exampleNote = new Note
        {
            Id = "2fefa629-1c28-420e-9309-fe784a6ed984",
            Timestamp = 67,
            Title = "Example title here",
            Description = "Lorem ipsum"
        };
        string serialized = JsonSerializer.Serialize(exampleNote);
        serialized.Should().Be($"{{\"id\":\"{exampleNote.Id}\",\"timestamp\":{exampleNote.Timestamp},\"title\":\"{exampleNote.Title}\",\"description\":\"{exampleNote.Description}\"}}");
        Note roundTrip = JsonSerializer.Deserialize<Note>(serialized);
        exampleNote.Should().BeEquivalentTo(roundTrip);
    }
}
