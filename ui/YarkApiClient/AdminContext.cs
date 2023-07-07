namespace YarkApiClient;

public class AdminContext : Context
{
    public string Secret { get; set; }

    public AdminContext(string secret, string baseUrl = "http://127.0.0.1:7776")
    {
        Secret = secret;
        BaseUrl = baseUrl;
    }
}