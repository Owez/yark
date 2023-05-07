use crate::{date::YarkDate, elements::Elements, note::Note};
use serde::{Deserialize, Serialize};

/// Single video inside of an archive which tracks a video's entire metadata history
#[derive(Debug, PartialEq, Clone, Serialize, Deserialize)]
pub struct Video {
    /// YouTube-provided identifier of this video
    pub id: String,
    /// Date this video was uploaded (typically to the nearest day)
    pub uploaded: YarkDate,
    /// Width hint of the downloaded video
    #[deprecated(since = "3.1.0-beta.1", note = "Will be removed in v4")]
    pub width: u32,
    /// Height hint of the downloaded video
    #[deprecated(since = "3.1.0-beta.1", note = "Will be removed in v4")]
    pub height: u32,
    /// Known titles which the video has had
    pub title: Elements<String>,
    /// Known descriptions which the video has had
    pub description: Elements<String>,
    /// Known view counts which the video has had
    pub views: Elements<Option<u32>>,
    /// Known like counts which the video has had
    pub likes: Elements<Option<u32>>,
    /// Known thumbnails which the video has had; see [Thumbnails]
    pub thumbnail: Thumbnails,
    /// Status history of the video indicating the time(s) it's been removed from public consumption (privated/deleted)
    pub deleted: Elements<bool>,
    /// User-written notes attached to the video; see [Note]
    pub notes: Vec<Note>,
}

impl Video {
    /// Creates a new video with all values provided to be known about just now (i.e. values have just been found out)
    #[allow(deprecated)]
    pub fn new(
        id: String,
        uploaded: YarkDate,
        width: u32,
        height: u32,
        title: String,
        description: String,
        views: Option<u32>,
        likes: Option<u32>,
        thumbnail: String,
    ) -> Self {
        Self {
            id,
            uploaded,
            width,
            height,
            title: Elements::new_now(title),
            description: Elements::new_now(description),
            views: Elements::new_now(views.into()),
            likes: Elements::new_now(likes.into()),
            thumbnail: Thumbnails::new_now(thumbnail),
            deleted: Elements::new_now(false),
            notes: vec![],
        }
    }
}

/// Wrapper around [Elements] of thumbnail hashes; this structure can be used to pull the image files from the archive directory
#[derive(Debug, PartialEq, Clone, Serialize, Deserialize)]
pub struct Thumbnails(pub Elements<String>);

impl Thumbnails {
    /// Creates a new thumbnails tracker with the first hash assuming it's been found out about just now
    pub fn new_now(hash: String) -> Self {
        Self(Elements::new_now(hash))
    }

    /// Inserts a new hash which has been found out about just now
    pub fn insert_now(&mut self, hash: String) {
        self.0.insert_now(hash)
    }

    /// Inserts a new hash with a corresponding [YarkDate] for existing thumbnails
    pub fn insert(&mut self, dt: YarkDate, hash: String) {
        self.0.insert(dt, hash);
    }
}

impl Default for Thumbnails {
    fn default() -> Self {
        Self(Elements::default())
    }
}
