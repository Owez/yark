<!-- TODO: logo -->
<!-- TODO: add when logos done: <h1 align="center">yark</h1> -->

# yark

YouTube archiving made simple.

- [yark](#yark)
  - [Installation](#installation)
  - [Creating an Archive](#creating-an-archive)
  - [Viewing an Archive](#viewing-an-archive)

Yark lets you continuously archive all videos and metadata of a channel. You can also view your archive as a seemless offline website 🦾

## Installation

To install yark, simply download it off of PyPI:

```shell
$ pip3 install yark
```

## Creating an Archive


Once you've installed yark, think of a name for your archive and copy the target's channel id:

```shell
$ yark new owez UCSMdm6bUYIBN0KfS2CVuEPA
```

Now that you've created the archive, you can tell yark to download all videos and metadata:

```shell
$ yark refresh owez
```

Here's what my channel looked like after following the steps (if anything was updated/deleted it would be blue/red to indicate):

<p><img src="examples/reportadd.png" alt="Demonstration" title="Demonstration" width="400" /></p>

<!-- TODO: new demo, this one doesn't include video downloading. maybe include blue/red -->

Right now scheduling isn't a feature so to run the archiver every now and then please use [`cron`](https://en.wikipedia.org/wiki/Cron) or something similar. Once a day is recommended because getting metadata takes ages!

## Viewing an Archive

<!-- TODO: fill out once developed -->
