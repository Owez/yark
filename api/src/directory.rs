//! Filesystem access for sensitive listing; see [Directory] for more info

use crate::errors::{Error, Result};
use serde::Serialize;
use std::{ffi::OsStr, fs, path::PathBuf};

/// Directory containing many [items](DirectoryItem) which lists a given directory
#[derive(Serialize)]
pub struct Directory {
    pub path: PathBuf,
    pub files: Vec<DirectoryItem>,
}

impl Directory {
    /// Creates a new directory listing by querying `path` provided
    pub fn new(path: PathBuf) -> Result<Self> {
        if !path.exists() || path.is_file() {
            return Err(Error::DirectoryNotFound);
        }
        let paths = fs::read_dir(&path).map_err(|err| Error::DirectoryPath(err))?;
        let mut items = vec![];
        for path in paths {
            let entry = path.map_err(|err| Error::DirectoryPath(err))?;
            items.push(DirectoryItem::from(entry))
        }
        Ok(Self {
            path: path,
            files: items,
        })
    }
}

/// Single item inside of a [Directory] which could be an inner directory or a file
#[derive(Serialize)]
pub struct DirectoryItem {
    /// Path of this item
    pub path: PathBuf,
    /// Filename on the end of the full path for easy digestion
    pub filename: String,
    /// If this path is a directory or a file
    pub directory: bool,
    /// Marker of if this file/folder is hidden in normal file explorers
    pub hidden: bool,
    /// Marker of if this item is a compatible archive folder (i.e. contains a `yark.json` file inside)
    pub archive: bool,
}

impl From<fs::DirEntry> for DirectoryItem {
    fn from(entry: fs::DirEntry) -> Self {
        let path = entry.path();
        let filename = filename_to_string(path.file_name());
        DirectoryItem {
            directory: path.is_dir(),
            hidden: filename.starts_with("."),
            archive: is_path_archive(&path),
            path,
            filename,
        }
    }
}

fn filename_to_string(os_str_opt: Option<&OsStr>) -> String {
    os_str_opt
        .unwrap_or_default()
        .to_string_lossy()
        .into_owned()
}

fn is_path_archive(path: &PathBuf) -> bool {
    if path.is_file() {
        return false;
    }
    let archive_file_path = path.join("yark.json");
    return archive_file_path.exists();
}
