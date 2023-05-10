//! Crate-focused error and utility types such as the [Error] enum

use std::io;

use crate::ArchiveVersion;

/// Type cover for a result with an archive-focused [Error] enum
pub type Result<T> = std::result::Result<T, Error>;

/// Enumeration covering the possible errors which could occur during archive operations
#[derive(Debug)]
pub enum Error {
    /// An error occurred while attempting to load the archive/manager
    DataLoad(serde_json::Error),
    /// The archive was not found at the specified location
    ArchiveNotFound,
    /// The manager was not found at the specified location
    ManagerNotFound,
    /// The data (archive/manager) is corrupted and cannot be read
    DataCorrupted(io::Error),
    /// An error occurred while attempting to access the archive/manager path
    DataPath(io::Error),
    /// An error occurred while attempting to save the archive/manager
    DataSave(serde_json::Error),
    /// Version of a found archive/manager is incompatible with this crate's version
    IncompatibleVersion(ArchiveVersion),
}
