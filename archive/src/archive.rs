use crate::Video;
use uuid::Uuid;

pub struct Archive {
    pub id: Uuid,
    pub version: ArchiveVersion,
    pub url: String,
    pub videos: Vec<Video>,
    pub livestreams: Vec<Video>,
    pub shorts: Vec<Video>,
}

pub struct ArchiveVersion(u32);
