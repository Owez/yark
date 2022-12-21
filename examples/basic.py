from yark import Channel

# Create a new channel and refresh only it's metadata
Channel.new("demo", "https://www.youtube.com/channel/UCSMdm6bUYIBN0KfS2CVuEPA").metadata()

# Load the channel back up and do the same
channel = Channel.load("demo").metadata()

# Print all the video storage dictionary as a janky representation
print(channel.videos)

# Get a cool video I made and print it's description
video = channel.search("annp92OPZgQ")
print(video.description.current())
