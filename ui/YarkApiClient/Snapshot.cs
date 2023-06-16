namespace YarkApiClient;

public class Snapshot<T>
{
    public DateTime Taken { get; set; }
    public T Data { get; set; }

    public static Snapshot<T> NewEmpty()
    {
        return new Snapshot<T>
        {
            Taken = DateTime.MinValue,
            Data = default
        };
    }
}