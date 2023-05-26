//! Simple multi-archive manager; see [Manager] for more info

use crate::{
    archive::Archive,
    errors::{Error, Result},
    ArchiveVersion, DataSaveLoad, VERSION_COMPAT,
};
use serde::{Deserialize, Deserializer, Serialize, Serializer};
use std::{
    collections::HashMap,
    fs::{self, File},
    path::PathBuf,
};
use uuid::Uuid;

/// Collection of many opened archives which can be easily & quickly queried
///
/// # Explanation
///
/// The intended use-case for this manager is to:
///
/// 1. Store archives in the manager
/// 2. [Save](Self::save) the manager to a file when it's not needed
/// 3. [Load](Self::load) it back up again to retain the same identifiers
/// 4. Keep using the archives in the manager
///
/// This data structure acts as a *permanent* curator of multiple archives and attaches a unique identifier for every archive stored. Under the hood, this manager is a [HashMap] containing the identifier as a key and the archive as the value.
///
/// # Example
///
/// ```no_run
/// use std::path::PathBuf;
/// use yark_archive::prelude::*;
///
/// // Create a few archives
/// let archive_path = PathBuf::from("/path/to/archive");
/// let youtube_url = "https://www.youtube.com/channel/.."
/// let archive_alpha = Archive::new(archive_path.clone(), youtube_url.clone());
/// let archive_bravo = Archive::new(archive_path.clone(), youtube_url.clone());
/// let archive_charlie = Archive::new(archive_path, youtube_url);
///
/// // Create a manager & add new archives
/// let mut manager = Manager::default();
/// let alpha_id = manager.insert_new(archive_alpha);
/// let bravo_id = manager.insert_new(archive_bravo);
///
/// // Query for alpha
/// let alpha_query = manager.get(&alpha_id);
/// assert!(alpha_query.is_some()); // Some(&Archive)
///
/// // Delete bravo
/// manager.remove(&bravo_id);
///
/// // Query for deleted bravo
/// let bravo_query = manager.get(&bravo_id);
/// assert!(bravo_query.is_none()); // None
/// ```
#[derive(Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct Manager {
    /// Path of the file to [save](Self::save) this manager to
    #[serde(skip)]
    pub path: PathBuf,
    /// Version of this manager; this aligns with the archive versions
    pub version: ArchiveVersion,
    /// Actual archive/identifier data
    #[serde(
        serialize_with = "serialize_data",
        deserialize_with = "deserialize_data"
    )]
    pub archives: HashMap<Uuid, Archive>,
}

impl Manager {
    /// Creates a new manager with the current archive spec version and no data; use [Self::save] to save
    pub fn new(path: PathBuf) -> Self {
        Self {
            path,
            ..Default::default()
        }
    }

    /// Inserts a brand new archive into the manager not previously known
    pub fn insert_new(&mut self, archive: Archive) -> Uuid {
        let id = Uuid::new_v4();
        self.insert_existing(id.clone(), archive);
        id
    }

    /// Inserts an existing archive with a prior identifier into the manager
    pub fn insert_existing(&mut self, id: Uuid, archive: Archive) {
        self.archives.insert(id, archive);
    }

    /// Checks all archives under the manager to make sure they're all compatible
    pub fn ensure_compat(&self) -> Result<()> {
        for archive in self.archives.values() {
            if archive.version != VERSION_COMPAT {
                return Err(Error::IncompatibleVersion(archive.version));
            }
        }
        Ok(())
    }

    /// Gets a reference to an archive by it's identifier
    pub fn get(&self, id: &Uuid) -> Option<&Archive> {
        self.archives.get(id)
    }

    /// Gets a mutable reference to an archive by it's identifier
    pub fn get_mut(&mut self, id: &Uuid) -> Option<&mut Archive> {
        self.archives.get_mut(id)
    }

    /// Removes an archive from the manager by it's identifier
    pub fn remove(&mut self, id: &Uuid) -> Option<Archive> {
        self.archives.remove(id)
    }
}

impl<'a> DataSaveLoad<'a> for Manager {
    fn load(path: PathBuf) -> Result<Self> {
        // Check path
        if !path.exists() {
            return Err(Error::ManagerNotFound);
        }

        // Load up manager file
        let manager_data = fs::read_to_string(path.clone()).map_err(|err| Error::DataPath(err))?;
        Self::from_data_str(path, &manager_data)
    }

    fn save(&self) -> Result<()> {
        let writer = File::create(self.path.clone()).map_err(|err| Error::DataPath(err))?;
        serde_json::to_writer(&writer, self).map_err(|err| Error::DataSave(err))
    }

    fn set_path(&mut self, path: PathBuf) {
        self.path = path
    }
}

impl Default for Manager {
    fn default() -> Self {
        Self {
            path: PathBuf::default(),
            version: VERSION_COMPAT,
            archives: HashMap::with_capacity(1),
        }
    }
}

/// Serializes [Manager] into data but with [Manager::data] having [PathBuf] instead of [Archive]
fn serialize_data<S: Serializer>(
    data: &HashMap<Uuid, Archive>,
    serializer: S,
) -> std::result::Result<S::Ok, S::Error> {
    let mut serializable_data = HashMap::new();
    for (uuid, archive) in data.iter() {
        serializable_data.insert(uuid, &archive.path);
    }
    serializable_data.serialize(serializer)
}

/// Deserializes [Manager] from data by loading up archives from paths present
fn deserialize_data<'de, D: Deserializer<'de>>(
    deserializer: D,
) -> std::result::Result<HashMap<Uuid, Archive>, D::Error> {
    let mut deserialized_data: HashMap<Uuid, PathBuf> = Deserialize::deserialize(deserializer)?;
    let mut data = HashMap::new();
    for (uuid, path) in deserialized_data.drain() {
        let archive = Archive::load(path.clone()).map_err(|err| {
            serde::de::Error::custom(format!(
                "failed to load '{}' archive, {}",
                path.display(),
                err
            ))
        })?;
        data.insert(uuid, archive);
    }
    Ok(data)
}
