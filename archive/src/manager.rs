//! Simple multi-archive manager, see [Manager] for more info

use crate::{
    archive::Archive,
    errors::{Error, Result},
    ArchiveVersion, DataSaveLoad, VERSION_COMPAT,
};
use serde::{Deserialize, Serialize};
use std::{
    collections::HashMap,
    fs::{self, File},
    path::PathBuf,
};
use uuid::Uuid;

/// Collection of many opened archives which can be easily & quickly queried
///
/// The intended use-case for this manager is to:
///
/// 1. Store archives in the manager
/// 2. [Save](Self::save) the manager to a file when it's not needed
/// 3. [Load](Self::load) it back up again to retain the same identifiers
/// 4. Keep using the archives in the manager
///
/// This data structure acts as a *permanent* curator of multiple archives and attaches a unique identifier for every archive stored. Under the hood, this manager is a [HashMap] containing the identifier as a key and the archive as the value.
#[derive(Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct Manager {
    /// Path of the file to [save](Self::save) this manager to
    #[serde(skip)]
    pub path: PathBuf,
    /// Version of this manager; this aligns with the archive versions
    pub version: ArchiveVersion,
    /// Actual archive/identifier data
    pub data: HashMap<Uuid, Archive>,
}

impl Manager {
    /// Inserts a brand new archive into the manager not previously known
    pub fn insert_new(&mut self, archive: Archive) {
        self.insert_existing(Uuid::new_v4(), archive)
    }

    /// Inserts an existing archive with a prior identifier into the manager
    pub fn insert_existing(&mut self, id: Uuid, archive: Archive) {
        self.data.insert(id, archive);
    }

    /// Checks all archives under the manager to make sure they're all compatible
    pub fn ensure_compat(&self) -> Result<()> {
        for archive in self.data.values() {
            if archive.version != VERSION_COMPAT {
                return Err(Error::IncompatibleVersion(archive.version));
            }
        }
        Ok(())
    }

    /// Gets a reference to an archive by it's identifier
    pub fn get(&self, id: &Uuid) -> Option<&Archive> {
        self.data.get(id)
    }

    /// Gets a mutable reference to an archive by it's identifier
    pub fn get_mut(&mut self, id: &Uuid) -> Option<&mut Archive> {
        self.data.get_mut(id)
    }

    /// Removes an archive from the manager by it's identifier
    pub fn remove(&mut self, id: &Uuid) -> Option<Archive> {
        self.data.remove(id)
    }
}

impl<'a> DataSaveLoad<'a> for Manager {
    fn load(path: PathBuf) -> Result<Self> {
        // Check path
        if !path.exists() {
            return Err(Error::ManagerNotFound);
        }

        // Load up manager file
        let manager_data =
            fs::read_to_string(path.clone()).map_err(|err| Error::DataCorrupted(err))?;
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
            data: HashMap::with_capacity(1),
        }
    }
}
