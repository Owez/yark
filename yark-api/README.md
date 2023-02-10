# Yark API

YouTube archiving made simple (REST API)

- [Yark API](#yark-api)
  - [End-user](#end-user)
  - [Development](#development)
  - [Routes](#routes)
    - [GET `/`](#get-)
    - [POST `/archive?intent`](#post-archiveintent)
    - [GET `/archive?slug&kind`](#get-archiveslugkind)
    - [GET `/thumbnail?archive_slug&id`](#get-thumbnailarchive_slugid)


## End-user

Want to deploy your own federated Yark instance to connect to? You can do it using Yark API + Docker ✨

TODO: add docker and then make this guide

## Development

To get this API setup, please first install Python 3.11 and make sure you've got Poetry installed. With these installed, you can download the dependencies for the API:

```shell
$ poetry install
```

Once you've got all of the dependencies installed, create a new `.env` file and put in some environment variables:

```env
YARK_DATABASE_URI=sqlite:///example.db
YARK_SECRET=supersecure
```

You now have everything installed and you're not ready to develop! Switch your IDE to use the newly-created virtual environment. To run the API in debug mode, just run the following:

```shell
$ poetry run poe dev
```

## Routes

This section is a guide of the routes inside of this API.

### GET `/`

This route will simply redirect to the GitHub repository page if a user accidentally lands here. Eventually this will redirect to the downloads page.

### POST `/archive?intent`

This route lets you create/import an archive if you're the admin of the API instance. To add an archive into the API, you must first give the intent in a query string:

- `intent=create`: Create a new archive
- `intent=existing`: Import an existing archive

You also have to supply a JSON body to provide further details:

```jsonc
{
    // Unique slug identifier
	"slug": "Cool Archive",
    // Local path to this archive
	"path": "/Users/owen/Projects/MainArchive",
    // The URL this archive targets
	"target": "https://www.youtube.com/channel/UCSMdm6bUYIBN0KfS2CVuEPA"
}
```

This route also requires a bearer token containing admin credentials. Once all of this is given, the API will create the archive in it's database and return you with an adjusted slug you should use as the "true" slug:

```jsonc
{
	"message": "Archive created",
	"slug": "cool-archive"
}
```

### GET `/archive?slug&kind`

This route gets a page of information for an existing archive and can be used by anyone. To use it, put the known slug of the archive you're trying to get from the API instance and the kind of video list you're trying to fetch:

- `kind=videos`: Get a list of all contentional videos
- `kind=livestreams`: Gets a list of all livestreams
- `kind=shorts`: Gets a list of all shorts

With these query args supplied, you might get an empty `[]` JSON response back, indicating that there where no videos to fetch. If not, you'll get something that looks like this:

```jsonc
[
    {
        "uploaded": "2005-07-28T00:00:00",
        "thumbnail_id": "..",
        "title": "Me at the zoo",
        "id": "dQw4w9WgXcQ",
    },
    {
        "uploaded": "2042-12-02T00:00:00",
        "thumbnail_id": "👀",
        "title": "Help me I'm stuck inside of this README",
        "id": "helphelphelp",
    },
]
```

Each of the thumbnail identifiers provided back here can be used to [get](#get-thumbnailarchive_slugid) thumbnails which is used commonly to visualize a list of videos to a user.

### GET `/thumbnail?archive_slug&id`

This route returns a thumbnail image for the provided archive slug identifier, as well as the thumbnail identifier. It's usually used in conjunction with [getting](#get-archiveslugkind) archives.
