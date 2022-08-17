# yark

YouTube archiving made simple.

Yark lets you continuously archive all videos and metadata of a channel. You can also view your archive as a seemless offline website 🦾

## Installation

To install yark, simply download it off of PyPI:

```shell
$ pip3 install yark
```

## Creating an Archive

<p><img src="examples/reportadd.png" alt="Demonstration" title="Demonstration" width="400" /></p>

Once you've installed yark, think of a name for your archive and copy the targets channel id:

```shell
$ yark new owez UCSMdm6bUYIBN0KfS2CVuEPA
```

Now that you've created the archive, you can tell yark to download all videos and metadata:

```shell
$ yark refresh owez
```

Right now scheduling isn't a feature so to run the archiver every now and then please use [`cron`](https://en.wikipedia.org/wiki/Cron) or something similar. Once a day is recommended because getting metadata takes ages!

## Viewing an Archive

TODO
