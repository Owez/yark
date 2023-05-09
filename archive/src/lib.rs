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
//! 4. [Error](crate::errors::Error) – The crate-wide error enumeration
//!
//! You can use the prelude (`use yark_archive::prelude::*`) to quickly import everything you need!

pub mod archive;
pub mod date;
pub mod elements;
pub mod errors;
pub mod note;
pub mod prelude;
pub mod video;
