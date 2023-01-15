from yark import Archive, Config
from pathlib import Path

# Create a new archive
archive = Archive.new(
    Path("demo"), "https://www.youtube.com/channel/UCSMdm6bUYIBN0KfS2CVuEPA"
)

# Create a config for metadata/video downloads
config = Config()
config.max_videos = 5
config.max_shorts = 10
config.submit()

# Refresh only metadata and commit to file
archive.metadata(config)
archive.commit()

# Load the archive back up from file for the fun of it
archive = Archive.load(Path("demo"))

# Print all the video id's of the archive
print(", ".join([id for id in archive.videos.inner.keys()]))

# Get a cool video I made and print it's description
video = archive.search("annp92OPZgQ")
print(video.description.current())

# Download the 5 most recent videos and 10 most recent shorts
archive.download(config)
