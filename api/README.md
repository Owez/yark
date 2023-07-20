# Yark API

REST API for web-based Yark instances

- [Yark API](#yark-api)
	- [Development](#development)
	- [Specification](#specification)
		- [GET `/`](#get-)
		- [POST 🔒 `/archive`](#post--archive)
		- [GET `/archive/:id`](#get-archiveid)
		- [GET `/archive/:id/videos?kind`](#get-archiveidvideoskind)
		- [DELETE 🔒 `/archive/:id`](#delete--archiveid)
		- [GET `/archive/:id/image/:id/file`](#get-archiveidimageidfile)
		- [GET `/archive/:id/video/:id`](#get-archiveidvideoid)
		- [GET `/archive/:id/video/:id/file`](#get-archiveidvideoidfile)
		- [POST 🔒 `/archive/:id/video/:id/note`](#post--archiveidvideoidnote)
		- [PATCH 🔒 `/archive/:id/video/:id/note/:id`](#patch--archiveidvideoidnoteid)
		- [DELETE 🔒 `/archive/:id/video/:id/note/:id`](#delete--archiveidvideoidnoteid)
		- [GET 🔒 `/fs`](#get--fs)


## Development

To get this API setup, please make sure you've got the development dependencies from the contributing file installed. Once you've got these installed, please make a new `.env` file with the admin secret being `dev` and whatever database path you'd like:

```env
YARK_ADMIN_SECRET=dev
YARK_MANAGER_PATH=manager.json
```
Now that that's all been setup, you can run your brand new development server with `cargo run` now 🎉

## Specification

*Yark API Specification – Draft of version 1 – Include it in semvar as `+apispec.1` if possible*

This section is a friendly guide for all of the routes inside of this API and acts as an ad-hoc specification for the API which routes should be developed off of. It won't be perfect so it's best to contact someone if there's some ambiguity/wrongness.

### GET `/`

This route will simply redirect to the GitHub repository page if a user accidentally lands here. Eventually this will redirect to the downloads page or a webapp page.

### POST 🔒 `/archive`

This route lets you create a completely new archive if you're the admin of the API instance. To add an archive into the API, you must supply a JSON body:

```jsonc
{
    // Save destination for this archive
	"path": "/Users/owen/Projects/MainArchive",
    // The URL this archive should target
	"target": "https://www.youtube.com/channel/UCSMdm6bUYIBN0KfS2CVuEPA",
}
```

This route also requires a bearer token containing admin credentials. Once all of this is given, the API will create the archive and return you with an id reflecting the archive:

```jsonc
{
	"message": "Archive created",
	"id": "uuid"
}
```

### POST 🔒 `/archive/import`

This route lets you import an archive currently saved on a local filepath, optionally allowing you to also specify an id for it so you can re-add previous archives. To import an archive into the API, you must supply a JSON body:

```jsonc
{
    // Local path to the existing archive
	"path": "/Users/owen/Projects/ExistingArchive",
	// Optional id if you'd like to re-add the archive's id
	"id": "uuid",
}
```

This route also requires a bearer token containing admin credentials. Once all of this is given, the API will create the archive and return you with an id reflecting the archive:

```jsonc
{
	"message": "Archive imported",
	"id": "uuid"
}
```

### GET `/archive/:id`

This route lets you get meta-infromation about an existing archive. To use it, just put the known id of the archive you're trying to get:

```jsonc
{
	// General info
	"id": "uuid",
	"version": 3,
	"url": "https://www.youtube.com/channel/UCSMdm6bUYIBN0KfS2CVuEPA",
	"videos_count": 3,
	"livestreams_count": 20,
	"shorts_count": 0
}
```

### GET `/archive/:id/videos?kind&page`

This route gets a list of videos for existing archive and can be used by anyone. To use it, put the known id of the archive you're trying to get and the kind of video list you're trying to fetch:

- `kind=videos`: Get a list of all contentional videos
- `kind=livestreams`: Gets a list of all livestreams
- `kind=shorts`: Gets a list of all shorts

Plus the page of videos to get (each page contains 50 videos) as a number, e.g. `&page=5` for the 5th page. With these query args supplied, you might get an empty `[]` JSON response back, indicating that there where no videos to fetch. If not you might get a videos list from the archive data, for example:

```jsonc
[
	// First video
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
	// Second video
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

Each of the thumbnail identifiers provided back can be used to [get](#get-archiveidimageidfile) thumbnails as always.

### DELETE 🔒 `/archive/:id`

This route allows you to delete an archive by it's previously-assigned identifier. This route requires admin credentials but doesn't need any extra JSON body, just send the request to the route and it should return with:

```jsonc
{
	"message": "Archive deleted"
}
```

### GET `/archive/:id/image/:id/file`

This route returns an image for the provided archive identifier, as well as the image identifier. It's usually used in conjunction with [getting](#get-archiveidkind) archives.

### GET `/archive/:id/video/:id`

This route gets information about a specific video, probably one that you found from a [video list](#get-archiveidkind). When you supply it with the archive identifier and the video's identifier, it'll return with archive information about the video. A full example of a return looks like this:

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
	"notes": []
}
```

### GET `/archive/:id/video/:id/file`

This route returns a raw video file for the provided archive identifier like how getting images works. It's usually used in conjunction with [getting](#get-archiveidkind) archives to actually view the video.

### POST 🔒 `/archive/:id/video/:id/note`

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

This will return a simple creation message with the ID to refer to in the future to delete notes (to get notes [get](#get-archiveidvideoid) the full video):

```json
{
	"message": "Note created",
	"id": "uuid4"
}
```

### PATCH 🔒 `/archive/:id/video/:id/note/:id`

This route lets you update an existing note, it requires authentication and a JSON body of what to update. Here's the complete request to update every item possible (to not update an item, just remove the line):

```jsonc
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
	"message": "Note updated"
}
```

### DELETE 🔒 `/archive/:id/video/:id/note/:id`

This route lets you delete an existing note, it just requires authentication and the note identifier in the url. Here's the response you should get if you made a successfully request:

```json
{
	"message": "Note deleted"
}
```

### POST 🔒 `/fs`

This route lets you explore content on the API instances local filesystem so that a web-based file explorer can be implemented. This route will open the directory and list all files/folders in the path provided as json content. There is no POST/DELETE/etc because the *only* other action any actor should be able to do on the filesystem is create new archives. 

This route is protected by an admin secret and is probably the most sensitive route in the API, but it's needed due to (good) security restrictions on `<input type="file">` in modern browsers. If you don't supply any JSON, the response will be the current user's home directory. Here's an example of the JSON body used to query for a path:

```jsonc
{
	// Path to query for
	"path": "/get/this/directory",
	// If you want to go up one directory from the path
	"up": false,
}
```

This will return a response of either not found (if the directory doesn't exist or isn't a directory) or a list of all of the filenames and directories for the directory. You can then use this information to query deeper into the filesystem:

```jsonc
{
	// Path of original query (or the home dir got by default)
	"path": "/Users/owen/",
	// Each returned object is a file/directory
	"files": [
		{
			"path": "/get/this/directory/.file.txt",
			"filename": "file.txt",
			"directory": false,
			"hidden": true,
			"archive": false
		},
		{
			"path": "/get/this/directory/other/",
			"filename": "other",
			"directory": true,
			"hidden": false,
			"archive": false
		},
		{
			"path": "/get/this/directory/myarchive/",
			"filename": "myarchive",
			"directory": true,
			"hidden": false,
			"archive": true
		},
		// etc..
	]
}
```