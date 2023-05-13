//! Filesystem access for sensitive listing; see [Directory] for more info

use crate::errors::{Error, Result};
use serde::Serialize;
use std::vec::IntoIter;
use std::{fs, path::PathBuf};

/// Directory containing many [items](DirectoryItem) which lists a given directory
#[derive(Serialize)]
pub struct Directory(pub Vec<DirectoryItem>);

impl Directory {
    /// Creates a new directory listing by querying `path` provided
    pub fn new(path: PathBuf) -> Result<Self> {
        if !path.exists() || path.is_dir() {
            return Err(Error::DirectoryNotFound);
        }
        let paths = fs::read_dir(path).map_err(|err| Error::DirectoryPath(err))?;
        let mut items = vec![];
        for path in paths {
            let entry = path.map_err(|err| Error::DirectoryPath(err))?;
            items.push(DirectoryItem::from(entry))
        }
        Ok(Self(items))
    }
}

impl IntoIterator for Directory {
    type Item = DirectoryItem;
    type IntoIter = IntoIter<Self::Item>;

    fn into_iter(self) -> Self::IntoIter {
        self.0.into_iter()
    }
}

/// Single item inside of a [Directory] which could be an inner directory or a file
#[derive(Serialize)]
pub struct DirectoryItem {
    /// Path of this item
    pub path: PathBuf,
    /// If this path is a directory or a file
    pub directory: bool,
}

impl From<fs::DirEntry> for DirectoryItem {
    fn from(entry: fs::DirEntry) -> Self {
        let path = entry.path();
        DirectoryItem {
            directory: path.is_dir(),
            path,
        }
    }
}
