namespace YarkApiClient;

// TODO: make into kv pair and then deserialize into this full class, it should be `k: v` not `Snapshot { Taken: k, Data: v }`
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