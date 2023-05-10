//! Crate-focused error and utility types such as the [Error] enum

use crate::{ArchiveVersion, VERSION_COMPAT};
use std::{fmt, io};

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
    /// An error occurred while attempting to access the archive/manager path
    DataPath(io::Error),
    /// An error occurred while attempting to save the archive/manager
    DataSave(serde_json::Error),
    /// Version of a found archive/manager is incompatible with this crate's version
    IncompatibleVersion(ArchiveVersion),
}

impl fmt::Display for Error {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Self::DataLoad(err) => write!(
                f,
                "could not load data because it was invalid/corrupted ({})",
                err
            ),
            Self::ArchiveNotFound => write!(f, "archive could not be found"), // could be dir or file or id
            Self::ManagerNotFound => write!(f, "manager file could not be found"),
            Self::DataPath(err) => write!(
                f,
                "could not access path or read from a file; check permissions ({})",
                err
            ),
            Self::DataSave(err) => write!(
                f,
                "could not save data because it was invalid/corrupted ({})",
                err
            ),
            Self::IncompatibleVersion(version) => write!(
                f,
                "version found was {} but we're only compatible with {}",
                version, VERSION_COMPAT
            ),
        }
    }
}
