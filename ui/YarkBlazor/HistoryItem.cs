using YarkApiClient;

namespace YarkBlazor;

public class HistoryItem<T>
{
    public required string Tag { get; set; }
    public required int TagIndex { get; set; }
    public required int TagCount { get; set; }
    public required DateTime DateTime { get; set; }
    public required T Data { get; set; }

    public static IEnumerable<HistoryItem<T>> ElementsToHistoryItems(string tag, Elements<T> elements)
    {
        int count = elements.Count();
        return elements.Select((el, index) => new HistoryItem<T>
        {
            Tag = tag,
            TagIndex = index,
            TagCount = count,
            DateTime = el.Key,
            Data = el.Value
        });
    }
}