use crate::{date::YarkDate, elements::Elements, note::Note};
use serde::{Deserialize, Serialize};

#[derive(Debug, PartialEq, Clone, Serialize, Deserialize)]
pub struct Video {
    pub id: String,
    pub uploaded: YarkDate,
    #[deprecated(since = "3.1.0", note = "Will be removed in v4")]
    pub width: u32,
    #[deprecated(since = "3.1.0", note = "Will be removed in v4")]
    pub height: u32,
    pub title: Elements<String>,
    pub description: Elements<String>,
    pub views: Elements<Option<u32>>,
    pub likes: Elements<Option<u32>>,
    pub thumbnail: Thumbnails,
    pub deleted: Elements<bool>,
    pub notes: Vec<Note>,
}

impl Video {
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

#[derive(Debug, PartialEq, Clone, Serialize, Deserialize)]
pub struct Thumbnails(pub Elements<String>);

impl Thumbnails {
    pub fn new_now(hash: String) -> Self {
        Self(Elements::new_now(hash))
    }

    pub fn insert_now(&mut self, hash: String) {
        self.0.insert_now(hash)
    }

    pub fn insert(&mut self, dt: YarkDate, hash: String) {
        self.0.insert(dt, hash);
    }
}

impl Default for Thumbnails {
    fn default() -> Self {
        Self(Elements::default())
    }
}
