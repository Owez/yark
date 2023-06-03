# Yark

Dead version of Yark which previously used to be the master branch. This branch included a new work-in-progress v4 archive format which has since been dropped.

## Notice

This branch used to be the master branch from January-June 2023. It was originally intended to be the upcoming version 1.3 for Yark, but it was superseeded by:

1. `v1.3-dead-sveltekit`: This was a version of v1.2 with a new viewer made with SvelteKit and no comment support, still using v3 archives
2. `v1.3`: This is the current development branch for Yark switching back to v3 archives

## What does this mean for you?

If you have been using this branch on your computer, your v4 archives (the ones with comments) will have to be downgraded to v3 archives so you're compatible with the new `v1.3` branch. To do this:

1. Make a backup of your current `yark.json` so you still have all your comments for potential future versions of Yark
2. Then, use <https://github.com/owez/yarkv4v3> to automatically downgrade your v4 archive to a v3 one

You can then use the new version of Yark :)
