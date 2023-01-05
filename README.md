<!-- TODO: logo; #2 <https://github.com/Owez/yark/issues/2> -->
<!-- TODO: add when logos done; #2 <https://github.com/Owez/yark/issues/2>: <h1 align="center">yark</h1> -->

# Yark

YouTube archiving made simple.

[Installation](#installation) · [Managing your Archive](#managing-your-archive) · [Viewing your Archive](#viewing-your-archive)

Yark lets you continuously archive all videos and metadata for YouTube channels. You can also view your archive as a seamless offline website ✨

## Installation

To install Yark, simply download Python 3.9+ and run the following:

```shell
$ pip3 install yark
```

## Managing your Archive

Once you've installed Yark, think of a name for your archive and copy the target's url:

```shell
$ yark new owez https://www.youtube.com/channel/UCSMdm6bUYIBN0KfS2CVuEPA
```

Now that you've created the archive, you can tell Yark to download all videos and metadata using the refresh command:

```shell
$ yark refresh owez
```

Once everything has been downloaded, Yark will automatically give you a status report of what's changed since the last refresh:

<p><img src="examples/image/../images/cli_dark.png" alt="Report Demo" title="Report Demo" width="600" /></p>

## Viewing your Archive

Viewing you archive is easy, just type `view` with your archives name:

```shell
$ yark view owez
```

This will pop up an offline website in your browser letting you watch all videos 🚀

<p><img src="https://raw.githubusercontent.com/Owez/yark/master/examples/images/viewer_light.png" alt="Viewer Demo" title="Viewer Demo" width=650 /></p>

Under each video is a rich history report filled with timelines and graphs, as well as a noting feature which lets you add timestamped and permalinked comments 👐

<p><img src="https://raw.githubusercontent.com/Owez/yark/master/examples/images/viewer_stats_light.png" alt="Viewer Demo – Stats" title="Viewer Demo – Stats" width=650 /></p>

Light and dark modes are both available and automatically apply based on the system's theme.

## Details

Here are some things to keep in mind when using Yark; the good and the bad:

- Don't create a new archive again if you just want to update it, Yark accumulates all new metadata for you via timestamps
- Feel free to suggest new features via the issues tab on this repository
- Scheduling isn't a feature just yet, please use [`cron`](https://en.wikipedia.org/wiki/Cron) or something similar!

## Archive Format

The archive format itself is simple and consists of a directory-based structure with a core metadata file and all thumbnail/video data in their own directories as typical files:

- `[name]/` – Your self-contained archive
  - `yark.json` – Archive file with all metadata
  - `yark.bak` – Backup archive file to protect against data damage
  - `videos/` – Directory containing all known videos
    - `[id].mp4` – Files containing video data for YouTube videos
  - `thumbnails/` – Directory containing all known thumbnails
    - `[hash].png` – Files containing thumbnails with it's BLAKE2 hash

It's best to take a few minutes to familiarize yourself with your archive by looking at files which look interesting to you in it, everything is quite readable.
