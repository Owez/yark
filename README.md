# Yark

This is the "clean" version of an upcoming rewrite of Yark. The new features include:

- Completely new GUI-focused viewing/management system
- Rewritten archival format in Rust
- Better specifications

Once ready, this and the old [`v1.2`](https://github.com/Owez/yark/tree/v1.2) branch before the rewrite will be merged together as a new [`v1.3`](TODO) branch. This is being done because the downloader (how videos are actually parsed and downloaded) hasn't been rewritten in Rust and I want to get the GUI released before doing so.

This is a big task and the resulting [`v1.3`](TODO) branch will be *very* messy with a lot of moving parts, so this branch will stay as the clean one with only the rewritten components inside of it, and will be the branch v1.4 and beyond is based on.
