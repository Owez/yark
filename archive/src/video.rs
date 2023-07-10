//! Video metadata logic containing the [Video] structure

use crate::{
    date::YarkDate,
    elements::Elements,
    images::{ImageHash, Images},
    note::Notes,
};
use serde::{Deserialize, Serialize};
use std::collections::HashMap;

/// Single video inside of an archive which tracks a video's entire metadata history
#[derive(Debug, PartialEq, Eq, Clone, Serialize, Deserialize)]
pub struct Video {
    /// YouTube-provided identifier of this video
    pub id: String,
    /// Date this video was uploaded (typically to the nearest day)
    pub uploaded: YarkDate,
    /// Width hint (in pixels) of the potentially downloaded video
    #[deprecated(
        since = "0.1.0+arcspec.3",
        note = "Sunsetting; no plan for removal yet (v5?)"
    )]
    pub width: u32,
    /// Height hint (in pixels) of the potentially downloaded video
    #[deprecated(
        since = "0.1.0+arcspec.3",
        note = "Sunsetting; no plan for removal yet (v5?)"
    )]
    pub height: u32,
    /// Known titles which the video has had
    pub title: Elements<String>,
    /// Known descriptions which the video has had
    pub description: Elements<String>,
    /// Known view counts which the video has had
    pub views: Elements<Option<u32>>,
    /// Known like counts which the video has had
    pub likes: Elements<Option<u32>>,
    /// Known thumbnails which the video has had
    pub thumbnail: Images,
    /// Status history of the video indicating the time(s) it's been removed from public consumption (privated/deleted)
    pub deleted: Elements<bool>,
    /// User-written notes attached to the video; see [Note](crate::note::Note)/[Notes]
    pub notes: Notes,
}

impl Video {
    /// Creates a new video with all values provided to be known about just now (i.e. values have just been found out)
    #[allow(deprecated)]
    pub fn new(
        id: impl Into<String>,
        uploaded: impl Into<YarkDate>,
        width: u32,
        height: u32,
        title: impl Into<String>,
        description: impl Into<String>,
        views: impl Into<Option<u32>>,
        likes: impl Into<Option<u32>>,
        thumbnail: impl Into<ImageHash>,
    ) -> Self {
        Self {
            id: id.into(),
            uploaded: uploaded.into(),
            width,
            height,
            title: Elements::new_now(title.into()),
            description: Elements::new_now(description.into()),
            views: Elements::new_now(views.into()),
            likes: Elements::new_now(likes.into()),
            thumbnail: Images::new_now(thumbnail.into()),
            deleted: Elements::new_now(false),
            notes: Notes::default(),
        }
    }
}

/// List of [Video] items which can be queried as a [HashMap]
#[derive(Debug, PartialEq, Eq, Clone)]

pub struct Videos(pub HashMap<String, Video>);

impl Videos {
    // Get a reference to the video associated with a given id
    pub fn get(&self, key: &str) -> Option<&Video> {
        self.0.get(key)
    }

    // Get a mutable reference to the video associated with a given id
    pub fn get_mut(&mut self, key: &str) -> Option<&mut Video> {
        self.0.get_mut(key)
    }

    // Insert a video into the collection
    pub fn insert(&mut self, video: Video) -> Option<Video> {
        self.0.insert(video.id.clone(), video)
    }

    // Remove the video associated with a given id
    pub fn remove(&mut self, id: &str) -> Option<Video> {
        self.0.remove(id)
    }

    // Check if the collection contains a video with the given id
    pub fn contains_key(&self, id: &str) -> bool {
        self.0.contains_key(id)
    }

    // Get the number of videos in the collection
    pub fn len(&self) -> usize {
        self.0.len()
    }

    // Check if the collection is empty
    pub fn is_empty(&self) -> bool {
        self.0.is_empty()
    }

    // Clear the collection, removing all videos
    pub fn clear(&mut self) {
        self.0.clear()
    }

    // Iterate over the video identifiers in the collection
    pub fn keys(&self) -> impl Iterator<Item = &String> {
        self.0.keys()
    }

    // Iterate over the videos in the collection
    pub fn values(&self) -> impl Iterator<Item = &Video> {
        self.0.values()
    }

    // Iterate over mutable references to the videos in the collection
    pub fn values_mut(&mut self) -> impl Iterator<Item = &mut Video> {
        self.0.values_mut()
    }

    // Iterate over the videos identifiers and videos in the collection
    pub fn iter(&self) -> impl Iterator<Item = (&String, &Video)> {
        self.0.iter()
    }

    /// Pagifies the videos list to the `page` desired, with each page being a max of `size` long
    pub fn pagify(self, page: usize, size: usize) -> Videos {
        // TODO: make this more efficient, this isn't good code but it works™️

        // Get start index and return nothing if there's no videos on the page
        let start_ind = page * size;
        if self.0.len() < start_ind {
            return Videos::default();
        }

        // Get all the videos as a vec (the id is inside of video anyway)
        let mut videos: Vec<Video> = self.0.into_values().collect();
        videos.sort_by_key(|item| item.uploaded);
        videos.reverse();

        // Get end indexes
        let end_ind = (page + 1) * size;
        let clamped_end_ind = end_ind.min(videos.len());

        // Select the videos in range
        let selected_videos: Vec<Video> = videos[start_ind..clamped_end_ind].to_vec();

        // Create a new HashMap using the selected videos
        let mut paginated_videos = HashMap::new();
        for video in selected_videos {
            paginated_videos.insert(video.id.clone(), video);
        }
        Videos(paginated_videos)
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
    use crate::archive::Archive;
    use chrono::prelude::*;
    use std::path::PathBuf;

    const OWEZ_VIDEOS_DATA: &str = r#"[{"id":"Jlsxl-1zQJM","uploaded":"2021-07-28T00:00:00","width":1280,"height":720,"title":{"2023-05-03T11:35:50.993963":"ArmA 3 replay 2021 07 28 13 58"},"description":{"2023-05-03T11:35:50.993966":""},"views":{"2023-05-03T11:35:50.993974":34},"likes":{"2023-05-03T11:35:50.993975":0},"thumbnail":{"2023-05-03T11:35:54.782905":"38552fc160089251e638457762f45dbff573c520"},"deleted":{"2023-05-03T11:35:54.782920":false},"notes":[]},{"id":"z6y0mx2flRY","uploaded":"2021-04-29T00:00:00","width":1920,"height":1080,"title":{"2023-05-03T11:35:54.783019":"GLORY TO ARSTOZKA"},"description":{"2023-05-03T11:35:54.783021":"quickly animated poster for graphics outcome"},"views":{"2023-05-03T11:35:54.783023":24},"likes":{"2023-05-03T11:35:54.783025":null},"thumbnail":{"2023-05-03T11:35:55.193654":"8706b76c30fd98551f9c5d246f7294ec173f1086"},"deleted":{"2023-05-03T11:35:55.193668":false},"notes":[]},{"id":"annp92OPZgQ","uploaded":"2021-01-04T00:00:00","width":2560,"height":1440,"title":{"2023-05-03T11:35:55.193818":"psychedelica."},"description":{"2023-05-03T11:35:55.193823":"trippy.\n\n\n\n\nmade with my https://github.com/owez/mkplay program. all revenue goes to artists if requested."},"views":{"2023-05-03T11:35:55.193824":91},"likes":{"2023-05-03T11:35:55.193827":1},"thumbnail":{"2023-05-03T11:35:59.093903":"6a5c95513799671d51f22776e648c56c24789402"},"deleted":{"2023-05-03T11:35:59.093915":false},"notes":[]},{"id":"Sl3XgtKYq4E","uploaded":"2021-01-02T00:00:00","width":2560,"height":1440,"title":{"2023-05-03T11:35:59.094000":"one more time."},"description":{"2023-05-03T11:35:59.094003":"another one.\n\n\n\n\nmade with https://github.com/owez/mkplay, all ad revenue goes to the creators when requested/took through copyright"},"views":{"2023-05-03T11:35:59.094005":51},"likes":{"2023-05-03T11:35:59.094007":3},"thumbnail":{"2023-05-03T11:35:59.483710":"3fe5be5ceacde668310ddcf4311d10fb72d54e11"},"deleted":{"2023-05-03T11:35:59.483724":false},"notes":[]},{"id":"iWJbkSCMQlg","uploaded":"2018-06-03T00:00:00","width":1152,"height":720,"title":{"2023-05-03T11:35:59.483813":"thank you gmod"},"description":{"2023-05-03T11:35:59.483815":"Just a normal day with a joop from hell."},"views":{"2023-05-03T11:35:59.483817":39},"likes":{"2023-05-03T11:35:59.483819":1},"thumbnail":{"2023-05-03T11:35:59.847311":"7658b9da282cec122cb03af02ac676442df58e34"},"deleted":{"2023-05-03T11:35:59.847323":false},"notes":[]}]"#;

    fn elements_new_existing<T>(dt: DateTime<Utc>, value: T) -> Elements<T> {
        let mut elements = Elements::default();
        elements.insert(dt, value);
        elements
    }

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
            thumbnail: Images(elements_new_existing(
                DateTime::<Utc>::parse_from_rfc3339("2023-05-03T11:35:54.782905+00:00").unwrap(),
                "38552fc160089251e638457762f45dbff573c520".to_string(),
            )),
            deleted: elements_new_existing(
                DateTime::<Utc>::parse_from_rfc3339("2023-05-03T11:35:54.782920+00:00").unwrap(),
                false,
            ),
            notes: Notes::default(),
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
            thumbnail: Images(elements_new_existing(
                DateTime::<Utc>::parse_from_rfc3339("2023-05-03T11:35:55.193654+00:00").unwrap(),
                "8706b76c30fd98551f9c5d246f7294ec173f1086".to_string(),
            )),
            deleted: elements_new_existing(
                DateTime::<Utc>::parse_from_rfc3339("2023-05-03T11:35:55.193668+00:00").unwrap(),
                false,
            ),
            notes: Notes::default(),
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
            thumbnail: Images(elements_new_existing(
                DateTime::<Utc>::parse_from_rfc3339("2023-05-03T11:35:59.093903+00:00").unwrap(),
                "6a5c95513799671d51f22776e648c56c24789402".to_string(),
            )),
            deleted: elements_new_existing(
                DateTime::<Utc>::parse_from_rfc3339("2023-05-03T11:35:59.093915+00:00").unwrap(),
                false,
            ),
            notes:Notes::default(),
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
            thumbnail: Images(elements_new_existing(
                DateTime::<Utc>::parse_from_rfc3339("2023-05-03T11:35:59.483710+00:00").unwrap(),
                "3fe5be5ceacde668310ddcf4311d10fb72d54e11".to_string(),
            )),
            deleted: elements_new_existing(
                DateTime::<Utc>::parse_from_rfc3339("2023-05-03T11:35:59.483724+00:00").unwrap(),
                false,
            ),
            notes:Notes::default(),
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
            thumbnail: Images(elements_new_existing(
                DateTime::<Utc>::parse_from_rfc3339("2023-05-03T11:35:59.847311+00:00").unwrap(),
                "7658b9da282cec122cb03af02ac676442df58e34".to_string(),
            )),
            deleted: elements_new_existing(
                DateTime::<Utc>::parse_from_rfc3339("2023-05-03T11:35:59.847323+00:00").unwrap(),
                false,
            ),
            notes: Notes::default(),
        });
        exp
    }

    #[test]
    fn videos_full_serde() {
        let videos = owez_exp(PathBuf::default()).videos;
        let converted = serde_json::to_string(&videos).expect("JSON conversion failed");
        let back: Videos = serde_json::from_str(&converted).expect("Videos back-into didn't work");
        assert_eq!(back, videos)
    }

    #[test]
    fn videos_deserializing() {
        let exp = owez_exp(PathBuf::default()).videos;
        let converted: Videos =
            serde_json::from_str(OWEZ_VIDEOS_DATA).expect("JSON conversion failed");
        assert_eq!(exp, converted);
    }

    #[test]
    fn pagification() {
        let video1 = Video {
            id: "1".to_string(),
            uploaded: Utc::now().into(),
            width: 1920,
            height: 1080,
            title: Elements::default(),
            description: Elements::default(),
            views: Elements::default(),
            likes: Elements::default(),
            thumbnail: Images::default(),
            deleted: Elements::default(),
            notes: Notes::default(),
        };

        let video2 = Video {
            id: "2".to_string(),
            uploaded: DateTime::<Utc>::MIN_UTC.into(),
            width: 1280,
            height: 720,
            title: Elements::default(),
            description: Elements::default(),
            views: Elements::default(),
            likes: Elements::default(),
            thumbnail: Images::default(),
            deleted: Elements::default(),
            notes: Notes::default(),
        };

        let video3 = Video {
            id: "3".to_string(),
            uploaded: Utc::now().into(),
            width: 1920,
            height: 1080,
            title: Elements::default(),
            description: Elements::default(),
            views: Elements::default(),
            likes: Elements::default(),
            thumbnail: Images::default(),
            deleted: Elements::default(),
            notes: Notes::default(),
        };

        let video4 = Video {
            id: "4".to_string(),
            uploaded: DateTime::<Utc>::MIN_UTC.into(),
            width: 1280,
            height: 720,
            title: Elements::default(),
            description: Elements::default(),
            views: Elements::default(),
            likes: Elements::default(),
            thumbnail: Images::default(),
            deleted: Elements::default(),
            notes: Notes::default(),
        };

        let videos_list = Videos(
            vec![
                ("1".to_string(), video1),
                ("2".to_string(), video2.clone()),
                ("3".to_string(), video3),
                ("4".to_string(), video4.clone()),
            ]
            .into_iter()
            .collect::<HashMap<String, Video>>(),
        );

        let paginated_videos = videos_list.pagify(1, 2);
        let expected_videos = Videos(
            vec![("2".to_string(), video2), ("4".to_string(), video4)]
                .into_iter()
                .collect::<HashMap<String, Video>>(),
        );

        assert_eq!(paginated_videos, expected_videos);
    }
}