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
        state::AppState,
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
        Extension(state): Extension<Arc<Mutex<AppState>>>,
        Json(schema): Json<CreateJsonSchema>,
    ) -> Result<Json<CreateResponse>> {
        debug!(
            "New archive creation request for '{}' channel at '{:?}' path",
            schema.target, schema.path
        );
        let archive = Archive::new(schema.path, schema.target);
        archive.save()?;
        let id = schema.id.unwrap_or(Uuid::new_v4());
        state.lock()?.manager.insert_existing(id, archive);
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
        Extension(state): Extension<Arc<Mutex<AppState>>>,
        Path(archive_id): Path<Uuid>,
        Query(GetQuerySchema { kind }): Query<GetQuerySchema>,
    ) -> Result<Json<Videos>> {
        debug!(
            "Getting a full list of videos for archive {} of kind TODO",
            archive_id
        );
        let state_lock = state.lock()?;
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
pub mod video {}

/// Note management as part of a parent note
pub mod note {}
