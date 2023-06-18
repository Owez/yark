using System.Text.Json;
using System.Text.Json.Serialization;

namespace YarkApiClient;

public class Elements<T>
{
    public Dictionary<DateTime, T> Values { get; set; }

    public Elements(Dictionary<DateTime, T> values)
    {
        Values = values;
    }

    public static Elements<T> NewTest(string isoDateString, T firstValue)
    {
        DateTime parsedDate = DateTime.Parse(isoDateString);
        Dictionary<DateTime, T> values = new Dictionary<DateTime, T>
        {
            { parsedDate, firstValue }
        };
        return new Elements<T>(values);
    }
}

// TODO: attach to json thing?
public class ElementsConverter<T> : JsonConverter<Elements<T>>
{
    public override Elements<T> Read(ref Utf8JsonReader reader, Type typeToConvert, JsonSerializerOptions options)
    {
        Dictionary<DateTime, T> values = new Dictionary<DateTime, T>();

        while (reader.Read())
        {
            if (reader.TokenType == JsonTokenType.EndObject)
            {
                break;
            }
            else if (reader.TokenType != JsonTokenType.PropertyName)
            {
                throw new JsonException("expected property name");
            }

            string propertyName = reader.GetString();
            DateTime date;

            if (!DateTime.TryParse(propertyName, out date))
            {
                throw new JsonException($"invalid date format: {propertyName}");
            }

            reader.Read();
            T value = JsonSerializer.Deserialize<T>(ref reader, options);

            values.Add(date, value);
        }

        return new Elements<T>(values);
    }

    public override void Write(Utf8JsonWriter writer, Elements<T> value, JsonSerializerOptions options)
    {
        writer.WriteStartObject();
        foreach (KeyValuePair<DateTime, T> kvp in value.Values)
        {
            string isoString = kvp.Key.ToString("o");
            writer.WritePropertyName(isoString);
            JsonSerializer.Serialize(writer, kvp.Value, options);
        }
        writer.WriteEndObject();
    }
}
