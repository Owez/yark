namespace YarkApiClient;

public class Elements<T> : Dictionary<DateTime, T>
{
    public static Elements<T> NewTest(string isoDateString, T firstValue)
    {
        DateTime parsedDate = DateTime.Parse(isoDateString);
        Elements<T> values = new Elements<T>
        {
            { parsedDate, firstValue }
        };
        return values;
    }

    public T? Current()
    {
        if (Count == 0)
        {
            return default;
        }
        DateTime mostRecentDate = Keys.OrderByDescending(k => k).First();
        return this[mostRecentDate];
    }
}
