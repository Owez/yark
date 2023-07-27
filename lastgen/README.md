# Yark Lastgen

Stripped down previous generation core/downloader/migrator logic for Yark

This directory contains essentially a cannibalised version of the previous `v1.2` release of Yark to be integrated into future versions. In versions like v1.3 and beyond the plan is to slowly rewrite this Python logic into Rust.

As yt-dlp, a core library for this project, presently does not have a god Rust wrapper, Python is a needed dependency. Therefore, Yark can safely rely on using some old messy code for the time being before it's migrated into the new core.