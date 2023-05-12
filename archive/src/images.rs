//! Image collection logic for archive-unique thumbnails etc; see [Images] for more info

use crate::{date::YarkDate, elements::Elements};
use serde::{Deserialize, Serialize};

/// Type cover for hashes of [Images] to use
pub type ImageHash = String;

/// Wrapper around [Elements] of image hashes; this structure can be used to pull the image files from the archive directory
#[derive(Debug, PartialEq, Eq, Clone, Serialize, Deserialize)]
pub struct Images(pub Elements<ImageHash>);

impl Images {
    /// Creates a new images tracker with the first hash assuming it's been found out about just now
    pub fn new_now(hash: ImageHash) -> Self {
        Self(Elements::new_now(hash))
    }

    /// Inserts a new hash which has been found out about just now
    pub fn insert_now(&mut self, hash: ImageHash) {
        self.0.insert_now(hash)
    }

    /// Inserts a new hash with a corresponding [YarkDate] for existing images
    pub fn insert(&mut self, dt: YarkDate, hash: ImageHash) {
        self.0.insert(dt, hash);
    }

    /// Returns the most recent image hash in the collection
    pub fn current(&self) -> Option<&ImageHash> {
        self.0.current()
    }
}

impl Default for Images {
    fn default() -> Self {
        Self(Elements::default())
    }
}
