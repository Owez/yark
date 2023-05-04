use std::io;

pub type Result<T> = std::result::Result<T, Error>;

#[derive(Debug)]
pub enum Error {
    ArchiveLoad(serde_json::Error),
    ArchiveNotFound,
    ArchiveCorrupted(io::Error),
    ArchivePath(io::Error),
    ArchiveSave(serde_json::Error),
}
