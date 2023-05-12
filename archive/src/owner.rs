//! Data representation for the playlist/channel; see [Channel]/[Playlist] for more info
//!
//! # Future
//!
//! This module will be merged into the [Archive](crate::archive::Archive) for the v4 archive specification (`+arcspec.4`) as a core part of the spec. For now it's made up by looking at what's on the fantastic [YouTube Metadata](https://mattw.io/youtube-metadata/) made by Matt Wright. There *will* be changes to this representation, so please don't standardize on it just yet.
//!
//! Because of the way that the API we hook onto works, playlists automatically give back channel information which is why in the future channels will *always* be returned, as well as the optional playlist information if the archive targets a playlist:
//!
//! ```no_run
//! struct Example {
//!     channel: Channel,
//!     playlist: Option<Playlist>
//! }
//! ```

use crate::{elements::Elements, images::Images};
use chrono::prelude::*;
use serde::{Deserialize, Serialize};

/// Representation of the channel data of the linked [Archive](crate::archive::Archive)
#[derive(Serialize, Deserialize)]
pub struct Channel {
    /// Name of the channel over time
    pub name: Elements<String>,
    /// Extended description over time
    pub description: Elements<String>,
    /// Avatar (profile picture) over time
    pub avatar: Images,
    /// Background banners over time
    pub banner: Images,
    /// Total view count over time
    pub views: Elements<u32>,
    /// Subscriber count over time
    pub subscribers: Elements<u32>,
    /// Date this channel was created
    pub created: DateTime<Utc>,
}

/// Representation of the playlist data of the linked [Archive](crate::archive::Archive)
#[derive(Serialize, Deserialize)]
pub struct Playlist {
    /// Name of the playlist over time
    pub name: Elements<String>,
    /// Extended description over time
    pub description: Elements<String>,
    /// Known *overall* thumbnails which the playlist has had
    pub thumbnail: Images,
    /// Date this playlist was created
    pub created: DateTime<Utc>,
}
