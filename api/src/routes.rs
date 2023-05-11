//! Route file containing all axum routes needed

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
    use crate::{
        errors::{Error, Result},
        state::{AppState, AppStateExtension},
    };
    use axum::{
        extract::{Path, Query},
        Extension, Json,
    };
    use log::debug;
    use serde::{Deserialize, Serialize};
    use std::{
        path::PathBuf,
        sync::{Arc, Mutex},
    };
    use uuid::Uuid;
    use yark_archive::prelude::*;

    #[derive(Deserialize)]
    pub struct CreateJsonSchema {
        path: PathBuf,
        target: String,
        id: Option<Uuid>,
    }

    #[derive(Serialize)]
    pub struct CreateResponse {
        message: &'static str,
        id: Uuid,
    }

    pub async fn create(
        Extension(state): Extension<AppStateExtension>,
        Json(schema): Json<CreateJsonSchema>,
    ) -> Result<Json<CreateResponse>> {
        debug!(
            "New archive creation request for '{}' channel at '{:?}' path",
            schema.target, schema.path
        );
        let archive = Archive::new(schema.path, schema.target);
        archive.save()?;
        let id = schema.id.unwrap_or(Uuid::new_v4());
        state.lock().await.manager.insert_existing(id, archive);
        Ok(Json(CreateResponse {
            message: "Archive created",
            id,
        }))
    }

    #[derive(Deserialize)]
    pub struct GetQuerySchema {
        kind: GetKind,
    }

    #[derive(Deserialize)]
    enum GetKind {
        #[serde(rename(deserialize = "videos"))]
        Videos,
        #[serde(rename(deserialize = "livestreams"))]
        Livestreams,
        #[serde(rename(deserialize = "shorts"))]
        Shorts,
    }

    pub async fn get(
        Extension(state): Extension<AppStateExtension>,
        Path(archive_id): Path<Uuid>,
        Query(GetQuerySchema { kind }): Query<GetQuerySchema>,
    ) -> Result<Json<Videos>> {
        debug!(
            "Getting a full list of videos for archive {} of kind TODO",
            archive_id
        );
        let state_lock = state.lock().await;
        let archive = state_lock
            .manager
            .get(&archive_id)
            .ok_or(Error::ArchiveNotFound)?;
        Ok(Json(match kind {
            GetKind::Videos => archive.videos.clone(),
            GetKind::Livestreams => archive.livestreams.clone(),
            GetKind::Shorts => archive.shorts.clone(),
        }))
    }
}

/// Video management as part of a parent archive
pub mod video {
    use crate::{
        errors::{Error, Result},
        state::AppStateExtension,
    };
    use axum::{
        extract::Path,
        response::{IntoResponse, Response},
        Extension, Json,
    };
    use axum_extra::body::AsyncReadBody;
    use hyper::header;
    use log::debug;
    use tokio::fs::File;
    use uuid::Uuid;
    use yark_archive::prelude::*;

    pub async fn get(
        Extension(state): Extension<AppStateExtension>,
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
        Extension(state): Extension<AppStateExtension>,
        Path((archive_id, video_id)): Path<(Uuid, Uuid)>,
    ) -> Result<Response> {
        debug!("Getting video {} file for archive {}", video_id, archive_id);
        let state_lock = state.lock().await;
        let archive = state_lock
            .manager
            .get(&archive_id)
            .ok_or(Error::ArchiveNotFound)?;
        let path = archive.path_video(&video_id).ok_or(Error::ImageNotFound)?;
        drop(state_lock);
        let file = File::open(path.clone())
            .await
            .map_err(|err| Error::FileShare(err))?;
        let headers = [(header::CONTENT_TYPE, "text/x-toml")]; // TODO: change
        let body = AsyncReadBody::new(file);
        Ok((headers, body).into_response())
    }
}

/// Note management as part of a parent note
pub mod note {}

/// Image file (e.g. thumbnails/profiles) sharing
pub mod image {
    use crate::{
        errors::{Error, Result},
        state::AppStateExtension,
    };
    use axum::{
        extract::Path,
        response::{IntoResponse, Response},
        Extension,
    };
    use axum_extra::body::AsyncReadBody;
    use hyper::header;
    use log::debug;
    use tokio::fs::File;
    use uuid::Uuid;

    pub async fn get_file(
        Extension(state): Extension<AppStateExtension>,
        Path((archive_id, image_hash)): Path<(Uuid, String)>,
    ) -> Result<Response> {
        debug!(
            "Getting image {} file for archive {}",
            image_hash, archive_id
        );
        let state_lock = state.lock().await;
        let archive = state_lock
            .manager
            .get(&archive_id)
            .ok_or(Error::ArchiveNotFound)?;
        let path = archive
            .path_image(&image_hash)
            .ok_or(Error::ImageNotFound)?;
        drop(state_lock);
        let file = File::open(path.clone())
            .await
            .map_err(|err| Error::FileShare(err))?;
        let headers = [(header::CONTENT_TYPE, "text/x-toml")]; // TODO: change
        let body = AsyncReadBody::new(file);
        Ok((headers, body).into_response())
    }
}
