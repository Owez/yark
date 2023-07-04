//! Route file containing all axum routes needed

use serde::Serialize;
use uuid::Uuid;

/// Generic response containing a simple message
#[derive(Serialize)]
pub struct MessageResponse {
    pub message: &'static str,
}

/// Generic response containing a simple message and unique identifier
#[derive(Serialize)]
pub struct MessageIdResponse {
    pub message: &'static str,
    pub id: Uuid,
}

/// Other/common routes which don't fit into other categories
pub mod misc {
    use axum::response::Redirect;

    /// Index page redirecting to Yark's GitHub
    pub async fn index() -> Redirect {
        Redirect::permanent("https://github.com/Owez/yark/")
    }
}

/// Base-level archive management into the manager
pub mod archive {
    use super::{MessageIdResponse, MessageResponse};
    use crate::{
        auth,
        errors::{Error, Result},
        state::AppStateExtension,
    };
    use axum::{
        extract::{Path, Query, State},
        Json,
    };
    use axum_auth::AuthBearer;
    use log::debug;
    use serde::{Deserialize, Serialize};
    use std::{fmt, path::PathBuf};
    use uuid::Uuid;
    use yark_archive::prelude::*;

    #[derive(Deserialize)]
    pub struct CreateJsonSchema {
        path: PathBuf,
        target: String,
        id: Option<Uuid>,
    }

    pub async fn create(
        State(state): State<AppStateExtension>,
        auth: AuthBearer,
        Json(schema): Json<CreateJsonSchema>,
    ) -> Result<Json<MessageIdResponse>> {
        debug!(
            "New archive creation request for '{}' channel at '{:?}' path",
            schema.target, schema.path
        );
        let mut state_lock = state.lock().await;
        auth::check(&state_lock.config, auth)?;
        let archive = Archive::new(schema.path, schema.target);
        archive.save()?;
        let id = schema.id.unwrap_or(Uuid::new_v4());
        state_lock.manager.insert_existing(id, archive);
        state_lock.manager.save()?;
        Ok(Json(MessageIdResponse {
            message: "Archive created",
            id,
        }))
    }

    #[derive(Serialize)]
    pub struct GetMetaResponse {
        id: Uuid,
        version: u32,
        url: String,
    }

    impl From<(Uuid, &Archive)> for GetMetaResponse {
        fn from((archive_id, archive): (Uuid, &Archive)) -> Self {
            Self {
                id: archive_id,
                version: archive.version,
                url: archive.url.clone(),
            }
        }
    }

    pub async fn get_meta(
        State(state): State<AppStateExtension>,
        Path(archive_id): Path<Uuid>,
    ) -> Result<Json<GetMetaResponse>> {
        debug!("Getting metadata for archive {}", archive_id);
        let state_lock = state.lock().await;
        let archive = state_lock
            .manager
            .get(&archive_id)
            .ok_or(Error::ArchiveNotFound)?;
        let archive_with_id = (archive_id, archive);
        Ok(Json(GetMetaResponse::from(archive_with_id)))
    }

    #[derive(Deserialize)]
    pub struct GetVideosQuerySchema {
        kind: GetVideoCollectionKind,
    }

    #[derive(Deserialize)]
    enum GetVideoCollectionKind {
        #[serde(rename(deserialize = "videos"))]
        Videos,
        #[serde(rename(deserialize = "livestreams"))]
        Livestreams,
        #[serde(rename(deserialize = "shorts"))]
        Shorts,
    }

    impl fmt::Display for GetVideoCollectionKind {
        fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
            match self {
                Self::Videos => write!(f, "videos"),
                Self::Livestreams => write!(f, "livestreams"),
                Self::Shorts => write!(f, "shorts"),
            }
        }
    }

    pub async fn get_videos(
        State(state): State<AppStateExtension>,
        Path(archive_id): Path<Uuid>,
        Query(GetVideosQuerySchema { kind }): Query<GetVideosQuerySchema>,
    ) -> Result<Json<Videos>> {
        debug!("Getting a full list of {} for archive {}", kind, archive_id);
        let state_lock = state.lock().await;
        let archive = state_lock
            .manager
            .get(&archive_id)
            .ok_or(Error::ArchiveNotFound)?;
        Ok(Json(match kind {
            GetVideoCollectionKind::Videos => archive.videos.clone(),
            GetVideoCollectionKind::Livestreams => archive.livestreams.clone(),
            GetVideoCollectionKind::Shorts => archive.shorts.clone(),
        }))
    }

    pub async fn delete(
        State(state): State<AppStateExtension>,
        Path(archive_id): Path<Uuid>,
        auth: AuthBearer,
    ) -> Result<Json<MessageResponse>> {
        debug!("Deleting archive {}", archive_id);
        let mut state_lock = state.lock().await;
        auth::check(&state_lock.config, auth)?;
        state_lock
            .manager
            .remove(&archive_id)
            .ok_or(Error::ArchiveNotFound)?;
        Ok(Json(MessageResponse {
            message: "Archive deleted",
        }))
    }
}

/// Image file (e.g. thumbnails/profiles) sharing
pub mod image {
    use crate::{
        errors::{Error, Result},
        state::AppStateExtension,
    };
    use axum::{
        body::{boxed, BoxBody},
        extract::{Path, State},
    };
    use hyper::{Body, Request, Response};
    use log::debug;
    use tower::util::ServiceExt;
    use tower_http::services::ServeFile;
    use uuid::Uuid;

    pub async fn get_file(
        State(state): State<AppStateExtension>,
        Path((archive_id, image_hash)): Path<(Uuid, String)>,
    ) -> Result<Response<BoxBody>> {
        debug!(
            "Getting image {} file for archive {}",
            image_hash, archive_id
        );
        let state_lock = state.lock().await;
        let archive = state_lock
            .manager
            .get(&archive_id)
            .ok_or(Error::ArchiveNotFound)?;
        let image_path = archive
            .path_image(&image_hash)
            .ok_or(Error::ImageNotFound)?;
        let req = Request::builder().body(Body::empty()).unwrap();
        let resp = ServeFile::new(image_path)
            .oneshot(req)
            .await
            .map_err(|err| Error::ImageFetch(err))?;
        Ok(resp.map(boxed))
    }
}

/// Video management as part of a parent archive
pub mod video {
    use crate::{
        errors::{Error, Result},
        state::AppStateExtension,
    };
    use axum::{
        body::{boxed, BoxBody},
        extract::{Path, State},
    };
    use axum::{response::Response, Json};
    use hyper::{Body, Request};
    use log::debug;
    use tower::util::ServiceExt;
    use tower_http::services::ServeFile;
    use uuid::Uuid;
    use yark_archive::prelude::*;

    pub async fn get(
        State(state): State<AppStateExtension>,
        Path((archive_id, video_id)): Path<(Uuid, String)>,
    ) -> Result<Json<Video>> {
        debug!(
            "Getting video {} details for archive {}",
            video_id, archive_id
        );
        let state_lock = state.lock().await;
        let archive = state_lock
            .manager
            .get(&archive_id)
            .ok_or(Error::ArchiveNotFound)?;
        if let Some(video) = archive.get_video(&video_id) {
            Ok(Json(video.to_owned()))
        } else {
            Err(Error::VideoNotFound)
        }
    }

    pub async fn get_file(
        State(state): State<AppStateExtension>,
        Path((archive_id, video_id)): Path<(Uuid, Uuid)>,
    ) -> Result<Response<BoxBody>> {
        debug!("Getting video {} file for archive {}", video_id, archive_id);
        let state_lock = state.lock().await;
        let archive = state_lock
            .manager
            .get(&archive_id)
            .ok_or(Error::ArchiveNotFound)?;
        let video_path = archive.path_video(&video_id).ok_or(Error::ImageNotFound)?;
        let req = Request::builder().body(Body::empty()).unwrap();
        let resp = ServeFile::new(video_path)
            .oneshot(req)
            .await
            .map_err(|err| Error::ImageFetch(err))?;
        Ok(resp.map(boxed))
    }
}

/// Note management as part of a parent note
pub mod note {
    use super::{MessageIdResponse, MessageResponse};
    use crate::{
        auth,
        errors::{Error, Result},
        state::AppStateExtension,
    };
    use axum::{
        extract::{Path, State},
        Json,
    };
    use axum_auth::AuthBearer;
    use log::debug;
    use serde::Deserialize;
    use uuid::Uuid;
    use yark_archive::prelude::Note;

    #[derive(Deserialize)]
    pub struct CreateJsonSchema {
        timestamp: u32,
        title: String,
        description: Option<String>,
    }

    pub async fn create(
        State(state): State<AppStateExtension>,
        Path((archive_id, video_id)): Path<(Uuid, String)>,
        auth: AuthBearer,
        Json(schema): Json<CreateJsonSchema>,
    ) -> Result<Json<MessageIdResponse>> {
        let note_id = Uuid::new_v4();
        debug!(
            "Creating new note {} for video {} in archive {}",
            note_id, video_id, archive_id
        );
        let mut state_lock = state.lock().await;
        auth::check(&state_lock.config, auth)?;
        let archive = state_lock
            .manager
            .get_mut(&archive_id)
            .ok_or(Error::ArchiveNotFound)?;
        let video = archive
            .get_video_mut(&video_id)
            .ok_or(Error::VideoNotFound)?;
        video.notes.insert(Note {
            id: note_id.clone(),
            timestamp: schema.timestamp,
            title: schema.title,
            description: schema.description,
        });
        Ok(Json(MessageIdResponse {
            message: "Note created",
            id: note_id,
        }))
    }

    #[derive(Deserialize)]
    pub struct UpdateJsonSchema {
        timestamp: Option<u32>,
        title: Option<String>,
        description: Option<Option<String>>,
    }

    pub async fn update(
        State(state): State<AppStateExtension>,
        Path((archive_id, video_id, note_id)): Path<(Uuid, String, Uuid)>,
        auth: AuthBearer,
        Json(schema): Json<UpdateJsonSchema>,
    ) -> Result<Json<MessageResponse>> {
        debug!(
            "Updating existing note {} for video {} in archive {}",
            note_id, video_id, archive_id
        );
        let mut state_lock = state.lock().await;
        auth::check(&state_lock.config, auth)?;
        let archive = state_lock
            .manager
            .get_mut(&archive_id)
            .ok_or(Error::ArchiveNotFound)?;
        let video = archive
            .get_video_mut(&video_id)
            .ok_or(Error::VideoNotFound)?;
        let note = video.notes.get_mut(&note_id).ok_or(Error::NoteNotFound)?;
        if let Some(timestamp) = schema.timestamp {
            note.timestamp = timestamp
        }
        if let Some(title) = schema.title {
            note.title = title
        }
        if let Some(description) = schema.description {
            note.description = description
        }
        Ok(Json(MessageResponse {
            message: "Note updated",
        }))
    }

    pub async fn delete(
        State(state): State<AppStateExtension>,
        Path((archive_id, video_id, note_id)): Path<(Uuid, String, Uuid)>,
        auth: AuthBearer,
    ) -> Result<Json<MessageResponse>> {
        debug!(
            "Deleting existing note {} for video {} in archive {}",
            note_id, video_id, archive_id
        );
        let mut state_lock = state.lock().await;
        auth::check(&state_lock.config, auth)?;
        let archive = state_lock
            .manager
            .get_mut(&archive_id)
            .ok_or(Error::ArchiveNotFound)?;
        let video = archive
            .get_video_mut(&video_id)
            .ok_or(Error::VideoNotFound)?;
        video.notes.remove(&note_id).ok_or(Error::NoteNotFound)?;
        Ok(Json(MessageResponse {
            message: "Note deleted",
        }))
    }
}

/// Sensitive filesystem routing for file exploration
pub mod fs {
    use crate::{auth, directory::Directory, errors::Result, state::AppStateExtension};
    use axum::{extract::State, Json};
    use axum_auth::AuthBearer;
    use serde::Deserialize;
    use std::path::PathBuf;

    #[derive(Deserialize)]
    pub struct GetJsonSchema {
        path: PathBuf,
    }

    pub async fn get(
        State(state): State<AppStateExtension>,
        auth: AuthBearer,
        Json(schema): Json<GetJsonSchema>,
    ) -> Result<Json<Directory>> {
        let state_lock = state.lock().await;
        auth::check(&state_lock.config, auth)?;
        Ok(Json(Directory::new(schema.path)?))
    }
}
