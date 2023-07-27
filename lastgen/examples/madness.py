from yark import Channel, DownloadConfig
from pathlib import Path

# Create a new channel
channel = Channel.new(
    Path("demo"), "https://www.youtube.com/channel/UCSMdm6bUYIBN0KfS2CVuEPA"
)

# Refresh only metadata and commit to file
channel.metadata()
channel.commit()

# Load the channel back up from file for the fun of it
channel = Channel.load(Path("demo"))

# Print all the video id's of the channel
print(", ".join([video.id for video in channel.videos]))

# Get a cool video I made and print it's description
video = channel.search("annp92OPZgQ")
print(video.description.current())

# Download the 5 most recent videos and 10 most recent shorts
config = DownloadConfig()
config.max_videos = 5
config.max_shorts = 10
config.submit()
channel.download(config)
