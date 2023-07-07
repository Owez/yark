using YarkApiClient;

public class Expected
{
    public static ArchiveMeta Meta()
    {
        return new ArchiveMeta
        {
            Id = "bc9f389d-275b-4500-9c36-85d46539b0d3",
            Version = 3,
            Url = "https://www.youtube.com/channel/UCSMdm6bUYIBN0KfS2CVuEPA"
        };
    }

    public static List<Video> Videos()
    {
        return new List<Video>
        {
            new Video
            {
                Id = "Jlsxl-1zQJM",
                Uploaded = DateTime.Parse("2021-07-28T00:00:00"),
                Width = 1280,
                Height = 720,
                Title = Elements<string>.NewTest("2023-05-03T11:35:50.993963", "ArmA 3 replay 2021 07 28 13 58"),
                Description = Elements<string>.NewTest("2023-05-03T11:35:50.993966", ""),
                Views = Elements<int?>.NewTest("2023-05-03T11:35:50.993974", 34),
                Likes = Elements<int?>.NewTest("2023-05-03T11:35:50.993975", 0),
                Thumbnail = Elements<string>.NewTest("2023-05-03T11:35:54.782905", "38552fc160089251e638457762f45dbff573c520"),
                Deleted = Elements<bool>.NewTest("2023-05-03T11:35:54.782920", false),
                Notes = new List<Note>(),
            },
            new Video
            {
                Id = "z6y0mx2flRY",
                Uploaded = DateTime.Parse("2021-04-29T00:00:00"),
                Width = 1920,
                Height = 1080,
                Title = Elements<string>.NewTest("2023-05-03T11:35:54.783019", "GLORY TO ARSTOZKA"),
                Description = Elements<string>.NewTest("2023-05-03T11:35:54.783021", "quickly animated poster for graphics outcome"),
                Views = Elements<int?>.NewTest("2023-05-03T11:35:54.783023", 24),
                Likes = Elements<int?>.NewTest("2023-05-03T11:35:54.783025", null),
                Thumbnail = Elements<string>.NewTest("2023-05-03T11:35:55.193654", "8706b76c30fd98551f9c5d246f7294ec173f1086"),
                Deleted = Elements<bool>.NewTest("2023-05-03T11:35:55.193668", false),
                Notes = new List<Note>(),
            },
            new Video
            {
                Id = "annp92OPZgQ",
                Uploaded = DateTime.Parse("2021-01-04T00:00:00"),
                Width = 2560,
                Height = 1440,
                Title = Elements<string>.NewTest("2023-05-03T11:35:55.193818", "psychedelica."),
                Description = Elements<string>.NewTest("2023-05-03T11:35:55.193823", "trippy.\n\n\n\n\nmade with my https://github.com/owez/mkplay program. all revenue goes to artists if requested."),
                Views = Elements<int?>.NewTest("2023-05-03T11:35:55.193824", 91),
                Likes = Elements<int?>.NewTest("2023-05-03T11:35:55.193827", 1),
                Thumbnail = Elements<string>.NewTest("2023-05-03T11:35:59.093903", "6a5c95513799671d51f22776e648c56c24789402"),
                Deleted = Elements<bool>.NewTest("2023-05-03T11:35:59.093915", false),
                Notes = new List<Note>(),
            },
            new Video
            {
                Id = "Sl3XgtKYq4E",
                Uploaded = DateTime.Parse("2021-01-02T00:00:00"),
                Width = 2560,
                Height = 1440,
                Title = Elements<string>.NewTest("2023-05-03T11:35:59.094000", "one more time."),
                Description = Elements<string>.NewTest("2023-05-03T11:35:59.094003", "another one.\n\n\n\n\nmade with https://github.com/owez/mkplay, all ad revenue goes to the creators when requested/took through copyright"),
                Views = Elements<int?>.NewTest("2023-05-03T11:35:59.094005", 51),
                Likes = Elements<int?>.NewTest("2023-05-03T11:35:59.094007", 3),
                Thumbnail = Elements<string>.NewTest("2023-05-03T11:35:59.483710", "3fe5be5ceacde668310ddcf4311d10fb72d54e11"),
                Deleted = Elements<bool>.NewTest("2023-05-03T11:35:59.483724", false),
                Notes = new List<Note>(),
            },
            new Video
            {
                Id = "iWJbkSCMQlg",
                Uploaded = DateTime.Parse("2018-06-03T00:00:00"),
                Width = 1152,
                Height = 720,
                Title = Elements<string>.NewTest("2023-05-03T11:35:59.483813", "thank you gmod"),
                Description = Elements<string>.NewTest("2023-05-03T11:35:59.483815", "Just a normal day with a joop from hell."),
                Views = Elements<int?>.NewTest("2023-05-03T11:35:59.483817", 39),
                Likes = Elements<int?>.NewTest("2023-05-03T11:35:59.483819", 1),
                Thumbnail = Elements<string>.NewTest("2023-05-03T11:35:59.847311", "7658b9da282cec122cb03af02ac676442df58e34"),
                Deleted = Elements<bool>.NewTest("2023-05-03T11:35:59.847323", false),
                Notes = new List<Note>(),
            }
        };
    }

    public static List<Video> Livestreams()
    {
        return new List<Video>();
    }

    public static List<Video> Shorts()
    {
        return new List<Video>();
    }
}
