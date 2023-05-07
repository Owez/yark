use std::io;

/// Type cover for a result with an archive-focused [Error] type
pub type Result<T> = std::result::Result<T, Error>;

/// Enumeration covering the possible errors which could occur during archive operations
#[derive(Debug)]
pub enum Error {
    /// An error occurred while attempting to load the archive
    ArchiveLoad(serde_json::Error),
    /// The archive was not found at the specified location
    ArchiveNotFound,
    /// The archive is corrupted and cannot be read
    ArchiveCorrupted(io::Error),
    /// An error occurred while attempting to access the archive path
    ArchivePath(io::Error),
    /// An error occurred while attempting to save the archive
    ArchiveSave(serde_json::Error),
}
