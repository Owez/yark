from yark import Channel, Maximums

# Create a new channel and refresh only it's metadata
Channel.new(
    "demo", "https://www.youtube.com/channel/UCSMdm6bUYIBN0KfS2CVuEPA"
).metadata()

# Load the channel back up and do the same
channel = Channel.load("demo")
channel.metadata()

# Save the metadata to file
channel.commit()

# Print all the video id's of the channel
print(", ".join([video.id for video in channel.videos]))

# Get a cool video I made and print it's description
video = channel.search("annp92OPZgQ")
print(video.description.current())

# Download the 5 most recent videos and 10 most recent shorts
maximums = Maximums()
maximums.videos = 5
maximums.shorts = 10
maximums.submit()
channel.download(maximums)
