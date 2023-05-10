# Yark API

REST API for web-based Yark instances

- [Yark API](#yark-api)
	- [Development](#development)
	- [Specification](#specification)
		- [GET `/`](#get-)
		- [POST `/archive`](#post-archive)
		- [GET `/archive/:id?kind`](#get-archiveidkind)
		- [GET `/archive/:slug/thumbnail/:id`](#get-archiveslugthumbnailid)
		- [GET `/archive/:slug/video/:id`](#get-archiveslugvideoid)
		- [GET `/archive/:slug/video/:video_id/file`](#get-archiveslugvideovideo_idfile)
		- [POST `/archive/:slug/video/:video_id/note`](#post-archiveslugvideovideo_idnote)
		- [PATCH `/archive/:slug/video/:video_id/note/:note_id`](#patch-archiveslugvideovideo_idnotenote_id)
		- [DELETE `/archive/:slug/video/:video_id/note/:note_id`](#delete-archiveslugvideovideo_idnotenote_id)


## Development

To get this API setup, please make sure you've got the development dependencies from the contributing file installed. Once you've got these installed, please make a new `.env` file with the admin secret being `dev` and whatever database path you'd like:

```env
YARK_ADMIN_SECRET=dev
YARK_MANAGER_PATH=manager.json
```

<!-- NOTE: not needed for rust rewrite -->
<!-- With these set, you need to migrate a new database for the API to use. To do this, launch the flask shell with `make flask_shell` and then type/copy-paste the following three commands:

```python
>>> from yark_api.extensions import *
>>> from yark_api.models import *
>>> db.create_all()
>>> exit()
``` -->

<!-- Now that the database has been migrated, you can run your brand new development server with `make dev` now 🎉 -->
Now that that's all been setup, you can run your brand new development server with `make dev` now 🎉

## Specification

*Draft of version 1 – Include it in semvar as `+apispec.1` if possible*

This section is a friendly guide for all of the routes inside of this API and acts as an ad-hoc specification for the API which routes should be developed off of. It won't be perfect so it's best to contact someone if there's some ambiguity/wrongness.

### GET `/`
<!-- SLUGGED -->

This route will simply redirect to the GitHub repository page if a user accidentally lands here. Eventually this will redirect to the downloads page or a webapp page.

### POST `/archive`
<!-- SLUGGED -->

This route lets you create/import an archive if you're the admin of the API instance. To add an archive into the API, you must supply a JSON body:

```jsonc
{
    // Local path to this archive
	"path": "/Users/owen/Projects/MainArchive",
    // The URL this archive targets
	"target": "https://www.youtube.com/channel/UCSMdm6bUYIBN0KfS2CVuEPA",
	// Optional identifier to set for this archive (only put this to re-add)
	"id": "existing-uuid"
}
```

This route also requires a bearer token containing admin credentials. Once all of this is given, the API will create the archive and return you with an id reflecting the archive:

```jsonc
{
	"message": "Archive created",
	"id": "uuid"
}
```

### GET `/archive/:id?kind`
<!-- SLUGGED -->

This route gets a page of information for an existing archive and can be used by anyone. To use it, put the known id of the archive you're trying to get and the kind of video list you're trying to fetch:

- `kind=videos`: Get a list of all contentional videos
- `kind=livestreams`: Gets a list of all livestreams
- `kind=shorts`: Gets a list of all shorts

With these query args supplied, you might get an empty `[]` JSON response back, indicating that there where no videos to fetch. If not you'll get a videos list from the archive data, for example:

```jsonc
[
	{
		"id": "Jlsxl-1zQJM",
		"uploaded": "2021-07-28T00:00:00",
		"width": 1280,
		"height": 720,
		"title": {
			"2023-05-03T11:35:50.993963": "ArmA 3 replay 2021 07 28 13 58"
		},
		"description": {
			"2023-05-03T11:35:50.993966": ""
		},
		// etc..
	},
	{
		"id": "z6y0mx2flRY",
		"uploaded": "2021-04-29T00:00:00",
		"width": 1920,
		"height": 1080,
		"title": {
			"2023-05-03T11:35:54.783019": "GLORY TO ARSTOZKA"
		},
		"description": {
			"2023-05-03T11:35:54.783021": "quickly animated poster for graphics outcome"
		},
		// etc..
	}
]
```

Each of the thumbnail identifiers provided back can be used to [get](#get-thumbnailarchive_slugid) thumbnails as always.

### GET `/archive/:slug/thumbnail/:id`

This route returns a thumbnail image for the provided archive slug identifier, as well as the thumbnail identifier. It's usually used in conjunction with [getting](#get-archiveslugkind) archives.

### GET `/archive/:slug/video/:id`

This route gets information about a specific video, probably one that you found from a [video list](#get-archiveidkind). When you supply it with the archive slug identifier and the video's identifier, it'll return with the raw archive information about the video.

This might change in the future, but as of now the raw JSON archive format has perfect compatibility with everything that needs to be displayed.

A full example of a return looks like this:

```json
{
	"uploaded": "2021-04-29T00:00:00",
	"width": 1920,
	"height": 1080,
	"title": {
		"2023-02-15T17:15:35.512302": "GLORY TO ARSTOZKA"
	},
	"description": {
		"2023-02-15T17:15:35.512305": "quickly animated poster for graphics outcome"
	},
	"views": {
		"2023-02-15T17:15:35.512307": 22
	},
	"likes": {
		"2023-02-15T17:15:35.512308": null
	},
	"thumbnail": {
		"2023-02-15T17:15:35.684134": "8706b76c30fd98551f9c5d246f7294ec173f1086"
	},
	"deleted": {
		"2023-02-15T17:15:35.684152": false
	},
	"comments": {},
	"notes": []
}
```

### GET `/archive/:slug/video/:video_id/file`

This route returns a raw video file for the provided archive slug identifier, as well as the video identifier. It's usually used in conjunction with [getting](#get-archiveslugkind) archives to actually view the video.

### POST `/archive/:slug/video/:video_id/note`

This route lets you add a new note to a video with all of it's required information filled out. You need to know at least the timestamp and the title of the note you'd like to put. You have to be authenticated to use this route. Here's an example of a full note's JSON body which you send as a request:

```jsonc
{
	// Main title
	"title": "Something cool here",
    // Video timestamp in seconds
	"timestamp": 120,
	// Optional description
	"body": "Optional body here, bigger than the title normally"
}
```

This will return a simple creation message with the ID to refer to in the future to delete notes (to get notes [get](#get-archiveslugvideoid) the full video):

```json
{
	"message": "Note created",
	"id": "uuid4"
}
```

### PATCH `/archive/:slug/video/:video_id/note/:note_id`

This route lets you update an existing note, it requires authentication and a JSON body of what to update. Here's the complete request to update every item possible (to not update an item, just remove the line):

```json
{
	// Main title
	"title": "New title for the note",
    // Video timestamp in seconds
	"timestamp": 30,
	// Optional description
	"body": "New big paragraph body for the note",
}
```

If this is sent to the API, the note will be updated and a simple message will be returned providing the status:

```json
{
	"message": "Note edited"
}
```

### DELETE `/archive/:slug/video/:video_id/note/:note_id`

This route lets you delete an existing note, it just requires authentication and the note identifier in the url. Here's the response you should get if you made a successfully request:

```json
{
	"message": "Note deleted"
}
```
