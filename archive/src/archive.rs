//! Archival core containing the top-level [Archive] structure

use crate::{
    errors::{Error, Result},
    video::Videos,
};
use serde::{Deserialize, Serialize};
use std::fs::{self, File};
use std::path::PathBuf;

#[derive(Debug, PartialEq, Serialize, Deserialize)]
pub struct Archive {
    /// Path of the directory where this archive exists and will [save](Self::save) to
    #[serde(skip)]
    pub path: PathBuf,
    /// Major version of this archive which indicates compatibility
    pub version: u32,
    /// URL of the YouTube channel or playlist this archive tracks
    pub url: String,
    /// Videos known to this archive; see [Videos] and [Video](crate::video::Video)
    pub videos: Videos,
    /// Livestreams known to this archive; see [Videos] and [Video](crate::video::Video)
    pub livestreams: Videos,
    /// Shorts known to this archive; see [Videos] and [Video](crate::video::Video)
    pub shorts: Videos,
}

impl Archive {
    /// Creates a new in-memory archive tied to the `path` provided
    pub fn new(path: PathBuf, url: String) -> Self {
        Self {
            path,
            version: 3,
            url,
            videos: Videos::default(),
            livestreams: Videos::default(),
            shorts: Videos::default(),
        }
    }

    /// Loads an existing archive from the `path` provided
    pub fn load(path: PathBuf) -> Result<Self> {
        // Get and check archive path
        let (archive_file_path, archive_file_path_exists) = archive_file_path(&path);
        if !archive_file_path_exists {
            return Err(Error::ArchiveNotFound);
        }

        // Load up archive file/data
        let archive_data =
            fs::read_to_string(archive_file_path).map_err(|err| Error::ArchiveCorrupted(err))?;
        Self::from_archive_str(path, &archive_data)
    }

    /// Saves the current archive to the [Self::path] directory
    pub fn save(&self) -> Result<()> {
        // Get file path and backup old if present
        let (archive_file_path, archive_file_path_exists) = archive_file_path(&self.path);
        if archive_file_path_exists {
            try_backup(&archive_file_path);
        }

        let writer = File::create(archive_file_path).map_err(|err| Error::ArchivePath(err))?;
        serde_json::to_writer(&writer, self).map_err(|err| Error::ArchiveSave(err))
    }

    /// Loads an archive from it's raw data and ties to the `path` provided for future use
    ///
    /// This is a helper function intended for advanced use. If you can, consider using [Self::load] instead.
    pub fn from_archive_str(path: PathBuf, archive_data: &str) -> Result<Self> {
        let mut archive: Self =
            serde_json::from_str(archive_data).map_err(|err| Error::ArchiveLoad(err))?;
        archive.path = path;
        Ok(archive)
    }

    /// Returns the raw archive data as a JSON string
    ///
    /// This is a helper function intended for advanced use. If you can, consider using [Self::save] instead.
    pub fn to_archive_str(&self) -> Result<String> {
        serde_json::to_string(self).map_err(|err| Error::ArchiveSave(err))
    }
}

/// Gets the `yark.json` from path given and says if it exists
fn archive_file_path(path: &PathBuf) -> (PathBuf, bool) {
    let mut archive_file_path = path.clone();
    archive_file_path.push("/yark.json");
    let exists = archive_file_path.exists();
    (archive_file_path, exists)
}

/// Try to backup previous `yark.json` file; gracefully fails if not
fn try_backup(archive_file_path: &PathBuf) {
    let mut backup = archive_file_path.clone();
    backup.pop();
    backup.push("yark.bak");
    fs::rename(archive_file_path, backup).ok();
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::{
        elements::Elements,
        video::{Thumbnails, Video},
    };
    use chrono::prelude::*;

    const OWEZ_DATA: &str = r#"{"version":3,"url":"https://www.youtube.com/channel/UCSMdm6bUYIBN0KfS2CVuEPA","videos":[{"id":"Jlsxl-1zQJM","uploaded":"2021-07-28T00:00:00","width":1280,"height":720,"title":{"2023-05-03T11:35:50.993963":"ArmA 3 replay 2021 07 28 13 58"},"description":{"2023-05-03T11:35:50.993966":""},"views":{"2023-05-03T11:35:50.993974":34},"likes":{"2023-05-03T11:35:50.993975":0},"thumbnail":{"2023-05-03T11:35:54.782905":"38552fc160089251e638457762f45dbff573c520"},"deleted":{"2023-05-03T11:35:54.782920":false},"notes":[]},{"id":"z6y0mx2flRY","uploaded":"2021-04-29T00:00:00","width":1920,"height":1080,"title":{"2023-05-03T11:35:54.783019":"GLORY TO ARSTOZKA"},"description":{"2023-05-03T11:35:54.783021":"quickly animated poster for graphics outcome"},"views":{"2023-05-03T11:35:54.783023":24},"likes":{"2023-05-03T11:35:54.783025":null},"thumbnail":{"2023-05-03T11:35:55.193654":"8706b76c30fd98551f9c5d246f7294ec173f1086"},"deleted":{"2023-05-03T11:35:55.193668":false},"notes":[]},{"id":"annp92OPZgQ","uploaded":"2021-01-04T00:00:00","width":2560,"height":1440,"title":{"2023-05-03T11:35:55.193818":"psychedelica."},"description":{"2023-05-03T11:35:55.193823":"trippy.\n\n\n\n\nmade with my https://github.com/owez/mkplay program. all revenue goes to artists if requested."},"views":{"2023-05-03T11:35:55.193824":91},"likes":{"2023-05-03T11:35:55.193827":1},"thumbnail":{"2023-05-03T11:35:59.093903":"6a5c95513799671d51f22776e648c56c24789402"},"deleted":{"2023-05-03T11:35:59.093915":false},"notes":[]},{"id":"Sl3XgtKYq4E","uploaded":"2021-01-02T00:00:00","width":2560,"height":1440,"title":{"2023-05-03T11:35:59.094000":"one more time."},"description":{"2023-05-03T11:35:59.094003":"another one.\n\n\n\n\nmade with https://github.com/owez/mkplay, all ad revenue goes to the creators when requested/took through copyright"},"views":{"2023-05-03T11:35:59.094005":51},"likes":{"2023-05-03T11:35:59.094007":3},"thumbnail":{"2023-05-03T11:35:59.483710":"3fe5be5ceacde668310ddcf4311d10fb72d54e11"},"deleted":{"2023-05-03T11:35:59.483724":false},"notes":[]},{"id":"iWJbkSCMQlg","uploaded":"2018-06-03T00:00:00","width":1152,"height":720,"title":{"2023-05-03T11:35:59.483813":"thank you gmod"},"description":{"2023-05-03T11:35:59.483815":"Just a normal day with a joop from hell."},"views":{"2023-05-03T11:35:59.483817":39},"likes":{"2023-05-03T11:35:59.483819":1},"thumbnail":{"2023-05-03T11:35:59.847311":"7658b9da282cec122cb03af02ac676442df58e34"},"deleted":{"2023-05-03T11:35:59.847323":false},"notes":[]}],"livestreams":[],"shorts":[]}"#;

    // TODO: merge with `video.rs` test
    fn elements_new_existing<T>(dt: DateTime<Utc>, value: T) -> Elements<T> {
        let mut elements = Elements::default();
        elements.insert(dt, value);
        elements
    }

    // TODO: merge with `video.rs` test
    #[allow(deprecated)]
    fn owez_exp(path: PathBuf) -> Archive {
        let mut exp = Archive::new(
            path,
            "https://www.youtube.com/channel/UCSMdm6bUYIBN0KfS2CVuEPA".to_string(),
        );
        exp.videos.insert(Video {
            id: "Jlsxl-1zQJM".to_string(),
            uploaded: DateTime::<Utc>::parse_from_rfc3339("2021-07-28T00:00:00+00:00")
                .unwrap()
                .into(),
            width: 1280,
            height: 720,
            title: elements_new_existing(
                DateTime::<Utc>::parse_from_rfc3339("2023-05-03T11:35:50.993963+00:00").unwrap(),
                "ArmA 3 replay 2021 07 28 13 58".to_string(),
            ),
            description: elements_new_existing(
                DateTime::<Utc>::parse_from_rfc3339("2023-05-03T11:35:50.993966+00:00").unwrap(),
                String::new(),
            ),
            views: elements_new_existing(
                DateTime::<Utc>::parse_from_rfc3339("2023-05-03T11:35:50.993974+00:00").unwrap(),
                Some(34),
            ),
            likes: elements_new_existing(
                DateTime::<Utc>::parse_from_rfc3339("2023-05-03T11:35:50.993975+00:00").unwrap(),
                Some(0),
            ),
            thumbnail: Thumbnails(elements_new_existing(
                DateTime::<Utc>::parse_from_rfc3339("2023-05-03T11:35:54.782905+00:00").unwrap(),
                "38552fc160089251e638457762f45dbff573c520".to_string(),
            )),
            deleted: elements_new_existing(
                DateTime::<Utc>::parse_from_rfc3339("2023-05-03T11:35:54.782920+00:00").unwrap(),
                false,
            ),
            notes: vec![],
        });
        exp.videos.insert(Video {
            id: "z6y0mx2flRY".to_string(),
            uploaded: DateTime::<Utc>::parse_from_rfc3339("2021-04-29T00:00:00+00:00")
                .unwrap()
                .into(),
            width: 1920,
            height: 1080,
            title: elements_new_existing(
                DateTime::<Utc>::parse_from_rfc3339("2023-05-03T11:35:54.783019+00:00").unwrap(),
                "GLORY TO ARSTOZKA".to_string(),
            ),
            description: elements_new_existing(
                DateTime::<Utc>::parse_from_rfc3339("2023-05-03T11:35:54.783021+00:00").unwrap(),
                "quickly animated poster for graphics outcome".to_string(),
            ),
            views: elements_new_existing(
                DateTime::<Utc>::parse_from_rfc3339("2023-05-03T11:35:54.783023+00:00").unwrap(),
                Some(24),
            ),
            likes: elements_new_existing(
                DateTime::<Utc>::parse_from_rfc3339("2023-05-03T11:35:54.783025+00:00").unwrap(),
                None,
            ),
            thumbnail: Thumbnails(elements_new_existing(
                DateTime::<Utc>::parse_from_rfc3339("2023-05-03T11:35:55.193654+00:00").unwrap(),
                "8706b76c30fd98551f9c5d246f7294ec173f1086".to_string(),
            )),
            deleted: elements_new_existing(
                DateTime::<Utc>::parse_from_rfc3339("2023-05-03T11:35:55.193668+00:00").unwrap(),
                false,
            ),
            notes: vec![],
        });
        exp.videos.insert(Video {
            id: "annp92OPZgQ".to_string(),
            uploaded: DateTime::<Utc>::parse_from_rfc3339("2021-01-04T00:00:00+00:00")
                .unwrap()
                .into(),
                width: 2560,
                height:1440,
            title: elements_new_existing(
                DateTime::<Utc>::parse_from_rfc3339("2023-05-03T11:35:55.193818+00:00").unwrap(),
                "psychedelica.".to_string(),
            ),
            description: elements_new_existing(
                DateTime::<Utc>::parse_from_rfc3339("2023-05-03T11:35:55.193823+00:00").unwrap(),
                "trippy.\n\n\n\n\nmade with my https://github.com/owez/mkplay program. all revenue goes to artists if requested.".to_string(),
            ),
            views: elements_new_existing(
                DateTime::<Utc>::parse_from_rfc3339("2023-05-03T11:35:55.193824+00:00").unwrap(),
                Some(91),
            ),
            likes: elements_new_existing(
                DateTime::<Utc>::parse_from_rfc3339("2023-05-03T11:35:55.193827+00:00").unwrap(),
                Some(1),
            ),
            thumbnail: Thumbnails(elements_new_existing(
                DateTime::<Utc>::parse_from_rfc3339("2023-05-03T11:35:59.093903+00:00").unwrap(),
                "6a5c95513799671d51f22776e648c56c24789402".to_string(),
            )),
            deleted: elements_new_existing(
                DateTime::<Utc>::parse_from_rfc3339("2023-05-03T11:35:59.093915+00:00").unwrap(),
                false,
            ),
            notes: vec![],
        }
        );
        exp.videos.insert(
            Video {
            id: "Sl3XgtKYq4E".to_string(),
            uploaded: DateTime::<Utc>::parse_from_rfc3339("2021-01-02T00:00:00+00:00")
                .unwrap()
                .into(),
                width: 2560,
                height:1440,
            title: elements_new_existing(
                DateTime::<Utc>::parse_from_rfc3339("2023-05-03T11:35:59.094000+00:00").unwrap(),
                "one more time.".to_string(),
            ),
            description: elements_new_existing(
                DateTime::<Utc>::parse_from_rfc3339("2023-05-03T11:35:59.094003+00:00").unwrap(),
                "another one.\n\n\n\n\nmade with https://github.com/owez/mkplay, all ad revenue goes to the creators when requested/took through copyright".to_string(),
            ),
            views: elements_new_existing(
                DateTime::<Utc>::parse_from_rfc3339("2023-05-03T11:35:59.094005+00:00").unwrap(),
                Some(51),
            ),
            likes: elements_new_existing(
                DateTime::<Utc>::parse_from_rfc3339("2023-05-03T11:35:59.094007+00:00").unwrap(),
                Some(3),
            ),
            thumbnail: Thumbnails(elements_new_existing(
                DateTime::<Utc>::parse_from_rfc3339("2023-05-03T11:35:59.483710+00:00").unwrap(),
                "3fe5be5ceacde668310ddcf4311d10fb72d54e11".to_string(),
            )),
            deleted: elements_new_existing(
                DateTime::<Utc>::parse_from_rfc3339("2023-05-03T11:35:59.483724+00:00").unwrap(),
                false,
            ),
            notes: vec![],
        }
        );
        exp.videos.insert(Video {
            id: "iWJbkSCMQlg".to_string(),
            uploaded: DateTime::<Utc>::parse_from_rfc3339("2018-06-03T00:00:00+00:00")
                .unwrap()
                .into(),
            width: 1152,
            height: 720,
            title: elements_new_existing(
                DateTime::<Utc>::parse_from_rfc3339("2023-05-03T11:35:59.483813+00:00").unwrap(),
                "thank you gmod".to_string(),
            ),
            description: elements_new_existing(
                DateTime::<Utc>::parse_from_rfc3339("2023-05-03T11:35:59.483815+00:00").unwrap(),
                "Just a normal day with a joop from hell.".to_string(),
            ),
            views: elements_new_existing(
                DateTime::<Utc>::parse_from_rfc3339("2023-05-03T11:35:59.483817+00:00").unwrap(),
                Some(39),
            ),
            likes: elements_new_existing(
                DateTime::<Utc>::parse_from_rfc3339("2023-05-03T11:35:59.483819+00:00").unwrap(),
                Some(1),
            ),
            thumbnail: Thumbnails(elements_new_existing(
                DateTime::<Utc>::parse_from_rfc3339("2023-05-03T11:35:59.847311+00:00").unwrap(),
                "7658b9da282cec122cb03af02ac676442df58e34".to_string(),
            )),
            deleted: elements_new_existing(
                DateTime::<Utc>::parse_from_rfc3339("2023-05-03T11:35:59.847323+00:00").unwrap(),
                false,
            ),
            notes: vec![],
        });
        exp
    }

    #[test]
    fn load_data_owez() {
        let dummy_path = PathBuf::default();
        match Archive::from_archive_str(dummy_path.clone(), OWEZ_DATA) {
            Ok(archive) => assert_eq!(archive, owez_exp(dummy_path)),
            Err(err) => panic!("Error from code: {:?}", err),
        }
    }

    #[test]
    fn load_data_owez_path() {
        let mut dummy_path = PathBuf::default();
        dummy_path.push("hello/world/this/is/a/test");
        match Archive::from_archive_str(dummy_path.clone(), OWEZ_DATA) {
            Ok(archive) => assert_eq!(archive, owez_exp(dummy_path)),
            Err(err) => panic!("Error from code: {:?}", err),
        }
    }

    #[test]
    fn owez_full_serde() {
        let dummy_path = PathBuf::default();
        let archive = owez_exp(dummy_path.clone());
        let serialized = archive
            .to_archive_str()
            .expect("Failed to convert to string");
        let back = Archive::from_archive_str(dummy_path, &serialized)
            .expect("Failed to convert back to archive");
        assert_eq!(archive, back);
    }
}
