<!-- TODO: logo; #2 <https://github.com/Owez/yark/issues/2> -->
<!-- TODO: add when logos done; #2 <https://github.com/Owez/yark/issues/2>: <h1 align="center">yark</h1> -->

# yark

YouTube archiving made simple.

- [yark](#yark)
  - [Installation](#installation)
  - [Managing your Archive](#managing-your-archive)
  - [Viewing your Archive](#viewing-your-archive)
  - [Details](#details)

Yark lets you continuously archive all videos and metadata of a channel. You can also view your archive as a seemless offline website 🦾

## Installation

To install yark, simply download Python 3.9+ and run the following:

```shell
$ pip3 install yark
```

## Managing your Archive


Once you've installed yark, think of a name for your archive and copy the target's channel id:

```shell
$ yark new owez UCSMdm6bUYIBN0KfS2CVuEPA
```

Now that you've created the archive, you can tell yark to download all videos and metadata:

```shell
$ yark refresh owez
```

Here's what my channel looked like after following the steps (if anything was updated/deleted it would be blue/red to indicate):

<p><img src="https://raw.githubusercontent.com/Owez/yark/master/examples/images/report.png" alt="Report Demo" title="Report Demo" width="600" /></p>

## Viewing your Archive

Viewing you archive is very simple, just type `view` and optionally the archive name:

```shell
$ yark view owez
```

This will pop up an offline website in your browser letting you watch all videos 🚀

<p><img src="https://raw.githubusercontent.com/Owez/yark/master/examples/images/channel.png" alt="Channel Demo" title="Channel Demo" /></p>

Under each video is a rich history report filled with graphs, as well as a noting feature which lets you add timestamped and permalinked comments 👐

<p><img src="https://raw.githubusercontent.com/Owez/yark/master/examples/images/history.png" alt="History Demo" title="History Demo" /></p>

## Details

Here are some things to keep in mind when using yark; the good and the bad:

- Don't create a new archive again if you just want to update it, yark accumulates all new metadata for you via timestamps
- Feel free to suggest new features via the issues tab on this repository
- Scheduling isn't a feature just yet, please use [`cron`](https://en.wikipedia.org/wiki/Cron) or something similar!
