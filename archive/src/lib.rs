//! Archiving core & utilities for the Yark archive format
//!
//! # What is it?
//!
//! Think of this crate as the low-level of interaction with the archive format, letting you implement higher-level logic on top of an unopinionated and *stable* core.
//!
//! This crate contains the basic underlying archive format for Yark and allows conversion to and from the archive file. It also contains utility/helper functions to easily query for saving images/videos, but doesn't have any logic or downloading interaction.
//!
//! # Example
//!
//! ```no_run
//! use yark_archive::prelude::*;
//! use std::path::PathBuf;
//! use chrono::prelude::*;
//!
//! // Create a new archive
//! let path = PathBuf::from("/my/archive/is/here");
//! let url = "https://www.youtube.com/channel/UCSMdm6bUYIBN0KfS2CVuEPA";
//! let mut archive = Archive::new(path.clone(), url.to_string());
//!
//! // Add a video and save
//! let video = Video::new(
//!     "Jlsxl-1zQJM",
//!     Utc.with_ymd_and_hms(2021, 7, 28, 0, 0, 0).unwrap(),
//!     1280,
//!     720,
//!     "Example Title",
//!     "Description here",
//!     Some(100),
//!     Some(12),
//!     "38552fc160089251e638457762f45dbff573c520",
//! );
//! archive.videos.insert(video);
//! archive.save().unwrap();
//!
//! // Load it up again
//! let new_archive = Archive::load(path).unwrap();
//! assert_eq!(archive, new_archive);
//! println!("Here it is: {:?}", new_archive);
//! ```
//!
//! # Common
//!
//! Here are the most common data structures you should check out to familiarize yourself with this crate:
//!
//! 1. [Archive](crate::archive::Archive) – Centerpiece of the crate
//! 2. [Video](crate::video::Video) – Single archived video in an archive
//! 3. [Elements](crate::elements::Elements) – Typical timestamped metadata storage
//! 4. [Manager](crate::manager::Manager) – Simple permanent multi-archive management
//! 4. [Error](crate::errors::Error) – The crate-wide error enumeration
//!
//! You can use the [prelude] module (`use yark_archive::prelude::*`) to quickly import everything you need!

pub mod archive;
pub mod date;
pub mod elements;
pub mod errors;
pub mod images;
pub mod manager;
pub mod note;
pub mod prelude;
pub mod video;

use errors::{Error, Result};
use serde::{Deserialize, Serialize};
use std::path::PathBuf;

/// Preferred type cover for archive versions
pub type ArchiveVersion = u32;

/// Version of the [ArchiveVersion] this version of the crate is compatible with
pub const VERSION_COMPAT: ArchiveVersion = 3;

/// API for the [Archive](crate::archive::Archive)/[Manager](crate::manager::Manager) which enables loading and saving
pub trait DataSaveLoad<'a>: Sized + Serialize + Deserialize<'a> {
    /// Loads an instance from the `path` provided
    fn load(path: PathBuf) -> Result<Self>;

    /// Saves the current instance to data store permanently
    fn save(&self) -> Result<()>;

    /// Sets path to save/load to (required due to lack of trait fields)
    fn set_path(&mut self, path: PathBuf);

    /// Loads from raw data and ties to the `path` provided for future use
    ///
    /// This is a helper function intended for advanced use. If you can, consider using [Self::load] instead.
    fn from_data_str(path: PathBuf, data: &'a str) -> Result<Self> {
        // NOTE: modified to add path
        let mut value: Self = serde_json::from_str(data).map_err(|err| Error::DataLoad(err))?;
        value.set_path(path);
        Ok(value)
    }

    /// Returns the raw data as a JSON string
    ///
    /// This is a helper function intended for advanced use. If you can, consider using [Self::save] instead.
    fn to_data_str(&self) -> Result<String> {
        serde_json::to_string(self).map_err(|err| Error::DataSave(err))
    }
}
