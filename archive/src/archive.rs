use crate::{
    errors::{Error, Result},
    video::Video,
};
use serde::{Deserialize, Serialize};
use std::path::PathBuf;
use std::{
    collections::HashMap,
    fs::{self, File},
};

#[derive(Debug, PartialEq, Serialize, Deserialize)]
pub struct Archive {
    #[serde(skip)]
    pub path: PathBuf,
    pub version: u32,
    pub url: String,
    pub videos: Videos,
    pub livestreams: Videos,
    pub shorts: Videos,
}

impl Archive {
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

    pub fn save(&self) -> Result<()> {
        // Get file path and backup old if present
        let (archive_file_path, archive_file_path_exists) = archive_file_path(&self.path);
        if archive_file_path_exists {
            try_backup(&archive_file_path);
        }

        let writer = File::create(archive_file_path).map_err(|err| Error::ArchivePath(err))?;
        serde_json::to_writer(&writer, self).map_err(|err| Error::ArchiveSave(err))
    }

    pub fn load(path: PathBuf) -> Result<Self> {
        // Get and check archive path
        let (archive_file_path, archive_file_path_exists) = archive_file_path(&path);
        if !archive_file_path_exists {
            return Err(Error::ArchiveNotFound);
        }

        // Load up archive file/data
        let archive_data =
            fs::read_to_string(archive_file_path).map_err(|err| Error::ArchiveCorrupted(err))?;
        Self::load_archive_data(path, &archive_data)
    }

    pub fn load_archive_data(path: PathBuf, archive_data: &str) -> Result<Self> {
        let mut archive: Self =
            serde_json::from_str(archive_data).map_err(|err| Error::ArchiveLoad(err))?;
        archive.path = path;
        Ok(archive)
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

#[derive(Debug, PartialEq)]

pub struct Videos(pub HashMap<String, Video>);

impl Videos {
    pub fn get(&self, id: &str) -> Option<&Video> {
        self.0.get(id)
    }

    pub fn get_mut(&mut self, id: &str) -> Option<&mut Video> {
        self.0.get_mut(id)
    }

    pub fn insert(&mut self, video: Video) {
        self.0.insert(video.id.clone(), video);
    }
}

impl Default for Videos {
    fn default() -> Self {
        Self(HashMap::default())
    }
}

impl Serialize for Videos {
    fn serialize<S>(&self, serializer: S) -> std::result::Result<S::Ok, S::Error>
    where
        S: serde::Serializer,
    {
        let vec = self.0.values().cloned().collect::<Vec<_>>();
        vec.serialize(serializer)
    }
}

impl<'de> Deserialize<'de> for Videos {
    fn deserialize<D>(deserializer: D) -> std::result::Result<Self, D::Error>
    where
        D: serde::Deserializer<'de>,
    {
        let vec = Vec::<Video>::deserialize(deserializer)?;
        let mut map = HashMap::new();
        for video in vec {
            map.insert(video.id.clone(), video);
        }
        Ok(Videos(map))
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    const OWEZ_DATA: &str = r#"{"version":3,"url":"https://www.youtube.com/channel/UCSMdm6bUYIBN0KfS2CVuEPA","videos":[{"id":"Jlsxl-1zQJM","uploaded":"2021-07-28T00:00:00","width":1280,"height":720,"title":{"2023-05-03T11:35:50.993963":"ArmA 3 replay 2021 07 28 13 58"},"description":{"2023-05-03T11:35:50.993966":""},"views":{"2023-05-03T11:35:50.993974":34},"likes":{"2023-05-03T11:35:50.993975":0},"thumbnail":{"2023-05-03T11:35:54.782905":"38552fc160089251e638457762f45dbff573c520"},"deleted":{"2023-05-03T11:35:54.782920":false},"notes":[]},{"id":"z6y0mx2flRY","uploaded":"2021-04-29T00:00:00","width":1920,"height":1080,"title":{"2023-05-03T11:35:54.783019":"GLORY TO ARSTOZKA"},"description":{"2023-05-03T11:35:54.783021":"quickly animated poster for graphics outcome"},"views":{"2023-05-03T11:35:54.783023":24},"likes":{"2023-05-03T11:35:54.783025":null},"thumbnail":{"2023-05-03T11:35:55.193654":"8706b76c30fd98551f9c5d246f7294ec173f1086"},"deleted":{"2023-05-03T11:35:55.193668":false},"notes":[]},{"id":"annp92OPZgQ","uploaded":"2021-01-04T00:00:00","width":2560,"height":1440,"title":{"2023-05-03T11:35:55.193818":"psychedelica."},"description":{"2023-05-03T11:35:55.193823":"trippy.\n\n\n\n\nmade with my https://github.com/owez/mkplay program. all revenue goes to artists if requested."},"views":{"2023-05-03T11:35:55.193824":91},"likes":{"2023-05-03T11:35:55.193827":1},"thumbnail":{"2023-05-03T11:35:59.093903":"6a5c95513799671d51f22776e648c56c24789402"},"deleted":{"2023-05-03T11:35:59.093915":false},"notes":[]},{"id":"Sl3XgtKYq4E","uploaded":"2021-01-02T00:00:00","width":2560,"height":1440,"title":{"2023-05-03T11:35:59.094000":"one more time."},"description":{"2023-05-03T11:35:59.094003":"another one.\n\n\n\n\nmade with https://github.com/owez/mkplay, all ad revenue goes to the creators when requested/took through copyright"},"views":{"2023-05-03T11:35:59.094005":51},"likes":{"2023-05-03T11:35:59.094007":3},"thumbnail":{"2023-05-03T11:35:59.483710":"3fe5be5ceacde668310ddcf4311d10fb72d54e11"},"deleted":{"2023-05-03T11:35:59.483724":false},"notes":[]},{"id":"iWJbkSCMQlg","uploaded":"2018-06-03T00:00:00","width":1152,"height":720,"title":{"2023-05-03T11:35:59.483813":"thank you gmod"},"description":{"2023-05-03T11:35:59.483815":"Just a normal day with a joop from hell."},"views":{"2023-05-03T11:35:59.483817":39},"likes":{"2023-05-03T11:35:59.483819":1},"thumbnail":{"2023-05-03T11:35:59.847311":"7658b9da282cec122cb03af02ac676442df58e34"},"deleted":{"2023-05-03T11:35:59.847323":false},"notes":[]}],"livestreams":[],"shorts":[]}"#;
    const OWEZ_VIDEOS_DATA: &str = r#"[{"id":"Jlsxl-1zQJM","uploaded":"2021-07-28T00:00:00","width":1280,"height":720,"title":{"2023-05-03T11:35:50.993963":"ArmA 3 replay 2021 07 28 13 58"},"description":{"2023-05-03T11:35:50.993966":""},"views":{"2023-05-03T11:35:50.993974":34},"likes":{"2023-05-03T11:35:50.993975":0},"thumbnail":{"2023-05-03T11:35:54.782905":"38552fc160089251e638457762f45dbff573c520"},"deleted":{"2023-05-03T11:35:54.782920":false},"notes":[]},{"id":"z6y0mx2flRY","uploaded":"2021-04-29T00:00:00","width":1920,"height":1080,"title":{"2023-05-03T11:35:54.783019":"GLORY TO ARSTOZKA"},"description":{"2023-05-03T11:35:54.783021":"quickly animated poster for graphics outcome"},"views":{"2023-05-03T11:35:54.783023":24},"likes":{"2023-05-03T11:35:54.783025":null},"thumbnail":{"2023-05-03T11:35:55.193654":"8706b76c30fd98551f9c5d246f7294ec173f1086"},"deleted":{"2023-05-03T11:35:55.193668":false},"notes":[]},{"id":"annp92OPZgQ","uploaded":"2021-01-04T00:00:00","width":2560,"height":1440,"title":{"2023-05-03T11:35:55.193818":"psychedelica."},"description":{"2023-05-03T11:35:55.193823":"trippy.\n\n\n\n\nmade with my https://github.com/owez/mkplay program. all revenue goes to artists if requested."},"views":{"2023-05-03T11:35:55.193824":91},"likes":{"2023-05-03T11:35:55.193827":1},"thumbnail":{"2023-05-03T11:35:59.093903":"6a5c95513799671d51f22776e648c56c24789402"},"deleted":{"2023-05-03T11:35:59.093915":false},"notes":[]},{"id":"Sl3XgtKYq4E","uploaded":"2021-01-02T00:00:00","width":2560,"height":1440,"title":{"2023-05-03T11:35:59.094000":"one more time."},"description":{"2023-05-03T11:35:59.094003":"another one.\n\n\n\n\nmade with https://github.com/owez/mkplay, all ad revenue goes to the creators when requested/took through copyright"},"views":{"2023-05-03T11:35:59.094005":51},"likes":{"2023-05-03T11:35:59.094007":3},"thumbnail":{"2023-05-03T11:35:59.483710":"3fe5be5ceacde668310ddcf4311d10fb72d54e11"},"deleted":{"2023-05-03T11:35:59.483724":false},"notes":[]},{"id":"iWJbkSCMQlg","uploaded":"2018-06-03T00:00:00","width":1152,"height":720,"title":{"2023-05-03T11:35:59.483813":"thank you gmod"},"description":{"2023-05-03T11:35:59.483815":"Just a normal day with a joop from hell."},"views":{"2023-05-03T11:35:59.483817":39},"likes":{"2023-05-03T11:35:59.483819":1},"thumbnail":{"2023-05-03T11:35:59.847311":"7658b9da282cec122cb03af02ac676442df58e34"},"deleted":{"2023-05-03T11:35:59.847323":false},"notes":[]}]"#;

    fn owez_exp(path: PathBuf) -> Archive {
        let mut exp = Archive::new(
            path,
            "https://www.youtube.com/channel/UCSMdm6bUYIBN0KfS2CVuEPA".to_string(),
        );
        exp.videos.insert(Video::new(
            "Jlsxl-1zQJM".to_string(),
            todo!(),
            "ArmA 3 replay 2021 07 28 13 58".to_string(),
            String::new(),
            Some(34),
            Some(0),
            "38552fc160089251e638457762f45dbff573c520".to_string(),
        ));
        exp.videos.insert(Video::new(
            "z6y0mx2flRY".to_string(),
            todo!(),
            "GLORY TO ARSTOZKA".to_string(),
            "quickly animated poster for graphics outcome".to_string(),
            Some(24),
            None,
            "8706b76c30fd98551f9c5d246f7294ec173f1086".to_string(),
        ));
        exp.videos.insert(Video::new( "annp92OPZgQ".to_string(),todo!(), "psychedelica.".to_string(),"trippy.\n\n\n\n\nmade with my https://github.com/owez/mkplay program. all revenue goes to artists if requested.".to_string(), Some(91),Some(1),"6a5c95513799671d51f22776e648c56c24789402".to_string()));
        exp.videos.insert(Video::new( "Sl3XgtKYq4E".to_string(),todo!(), "one more time.".to_string(),"another one.\n\n\n\n\nmade with https://github.com/owez/mkplay, all ad revenue goes to the creators when requested/took through copyright".to_string(), Some(51),Some(3),"3fe5be5ceacde668310ddcf4311d10fb72d54e11".to_string()));
        exp.videos.insert(Video::new(
            "iWJbkSCMQlg".to_string(),
            todo!(),
            "thank you gmod".to_string(),
            "Just a normal day with a joop from hell.".to_string(),
            Some(39),
            Some(1),
            "7658b9da282cec122cb03af02ac676442df58e34".to_string(),
        ));
        exp
    }

    #[test]
    fn load_data_owez() {
        let dummy_path = PathBuf::default();
        match Archive::load_archive_data(dummy_path.clone(), OWEZ_DATA) {
            Ok(archive) => assert_eq!(archive, owez_exp(dummy_path)),
            Err(err) => panic!("Error from code: {:?}", err),
        }
    }

    #[test]
    fn load_data_owez_path() {
        let mut dummy_path = PathBuf::default();
        dummy_path.push("hello/world/this/is/a/test");
        match Archive::load_archive_data(dummy_path.clone(), OWEZ_DATA) {
            Ok(archive) => assert_eq!(archive, owez_exp(dummy_path)),
            Err(err) => panic!("Error from code: {:?}", err),
        }
    }

    #[test]
    fn videos_serializing() {
        let videos = owez_exp(PathBuf::default()).videos;
        let converted = serde_json::to_string(&videos).expect("JSON conversion failed");
        assert_eq!(converted, OWEZ_VIDEOS_DATA)
    }

    #[test]
    fn videos_deserializing() {
        let exp = owez_exp(PathBuf::default()).videos;
        let converted: Videos =
            serde_json::from_str(OWEZ_VIDEOS_DATA).expect("JSON conversion failed");
        assert_eq!(exp, converted);
    }
}
