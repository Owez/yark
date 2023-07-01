using YarkBlazor;

public enum IconKind
{
    Placeholder,
    Dashboard,
    Videos,
    Livestreams,
    Shorts,
    Stars,
    Settings,
    Leave
}

public class IconKindMethods
{
    public static string GetUri(IconKind kind)
    {
        switch (kind)
        {
            case IconKind.Placeholder: return UriGenerator("Placeholder");
            case IconKind.Dashboard: return UriGenerator("Dashboard");
            case IconKind.Videos: return UriGenerator("Videos");
            case IconKind.Livestreams: return UriGenerator("Livestreams");
            case IconKind.Shorts: return UriGenerator("Shorts");
            case IconKind.Stars: return UriGenerator("Stars");
            case IconKind.Settings: return UriGenerator("Settings");
            case IconKind.Leave: return UriGenerator("Leave");
        }
        return UriGenerator("Placeholder");
    }

    private static string UriGenerator(string name)
    {
        return string.Format("/img/icons/{0} Icon.svg", name);
    }
}