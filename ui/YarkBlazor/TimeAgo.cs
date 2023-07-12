namespace YarkBlazor;

public class TimeAgo
{
    public DateTime DateTime;

    public TimeAgo(DateTime dateTime)
    {
        DateTime = dateTime;
    }

    public override string ToString()
    {
        // seconds
        DateTime oneMin = DateTime.UtcNow.AddMinutes(-1);
        if (DateTime >= oneMin)
        {
            TimeSpan intersection = DateTime.Subtract(oneMin);
            string plural = intersection.Seconds == 1 ? "" : "s";
            return String.Format("{0} second{1} ago", intersection.Seconds, plural);
        }
        // minutes
        DateTime oneHour = DateTime.UtcNow.AddHours(-1);
        if (DateTime >= oneHour)
        {
            TimeSpan intersection = DateTime.Subtract(oneHour);
            string plural = intersection.Minutes == 1 ? "" : "s";
            return String.Format("{0} minute{1} ago", intersection.Minutes, plural);
        }
        // hours
        DateTime oneDay = DateTime.UtcNow.AddDays(-1);
        if (DateTime >= oneDay)
        {
            TimeSpan intersection = DateTime.Subtract(oneDay);
            string plural = intersection.Hours == 1 ? "" : "s";
            return String.Format("{0} hour{1} ago", intersection.Hours, plural);
        }
        // days
        DateTime oneMonth = DateTime.UtcNow.AddMonths(-1);
        if (DateTime >= oneMonth)
        {
            TimeSpan intersection = DateTime.Subtract(oneMonth);
            string plural = intersection.Days == 1 ? "" : "s";
            return String.Format("{0} day{1} ago", intersection.Days, plural);
        }
        // months
        DateTime oneYear = DateTime.UtcNow.AddYears(-1);
        if (DateTime >= oneYear)
        {
            TimeSpan intersection = DateTime.Subtract(oneYear);
            int months = intersection.Days / 30;
            string plural = months == 1 ? "" : "s";
            return String.Format("{0} month{1} ago", months, plural);
        }
        // years
        else
        {
            DateTime now = DateTime.UtcNow;
            TimeSpan intersection = now.Subtract(DateTime);
            int years = intersection.Days / 365;
            string plural = years == 1 ? "" : "s";
            return String.Format("{0} year{1} ago", years, plural);
        }
    }
}