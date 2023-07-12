namespace YarkBlazor;

public enum IconKind
{
    Placeholder,
    Dashboard,
    Videos,
    Livestreams,
    Shorts,
    Stars,
    Settings,
    Leave,
    Back,
    GreenOrb,
    OrangeOrb,
    PurpleOrb
}

public class IconKindMethods
{
    public static string GetUri(IconKind kind)
    {
        switch (kind)
        {
            case IconKind.Placeholder: return TypicalUriGenerator("Placeholder");
            case IconKind.Dashboard: return TypicalUriGenerator("Dashboard");
            case IconKind.Videos: return TypicalUriGenerator("Videos");
            case IconKind.Livestreams: return TypicalUriGenerator("Livestreams");
            case IconKind.Shorts: return TypicalUriGenerator("Shorts");
            case IconKind.Stars: return TypicalUriGenerator("Stars");
            case IconKind.Settings: return TypicalUriGenerator("Settings");
            case IconKind.Leave: return TypicalUriGenerator("Leave");
            case IconKind.Back: return TypicalUriGenerator("Back");
            case IconKind.GreenOrb: return OrbUriGenerator("Green");
            case IconKind.OrangeOrb: return OrbUriGenerator("Orange");
            case IconKind.PurpleOrb: return OrbUriGenerator("Purple");
        }
        return TypicalUriGenerator("Placeholder");
    }

    private static string TypicalUriGenerator(string name)
    {
        return string.Format("/img/icons/{0} Icon.svg", name);
    }

    private static string OrbUriGenerator(string name)
    {
        return string.Format("/img/icons/{0} Orb.png", name);
    }
}