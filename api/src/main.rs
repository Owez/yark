//! REST API for web-based Yark instances

pub mod auth;
pub mod directory;
pub mod errors;
pub mod routes;
pub mod state;

use crate::errors::Result;
use crate::state::{AppStateExtension, Config};
use axum::routing::{delete, get, patch, post};
use axum::{Router, Server};
use dotenv::dotenv;
use errors::Error;
use log::info;
use state::AppState;
use std::fmt;
use std::path::PathBuf;
use std::process::exit;
use std::sync::Arc;
use tokio::sync::Mutex;
use tower_http::cors::CorsLayer;
use yark_archive::prelude::Manager;
use yark_archive::DataSaveLoad;

/// Main function which [launches](launch) the application
#[tokio::main]
async fn main() {
    info!("Starting Yark API");
    match launch().await {
        // All good and shutdown
        Ok(()) => (),
        // Startup errors
        Err(err) => err_exit(err),
    }
}

/// Exits program with fatal error message
fn err_exit(msg: impl fmt::Display) -> ! {
    eprintln!("Fatal error: {}", msg);
    exit(1)
}

/// Launches axum web server or fatally errors during the process
async fn launch() -> Result<()> {
    // Get dotenv file if possible
    dotenv().ok();

    // Get required preamble
    let config = Config::from_vars()?;
    let manager = get_manager(config.manager_path.clone())?;
    let addr = config.to_addr()?;

    // Log to user
    info!(
        "Launching at http://{}:{} address",
        config.host, config.port
    );

    // Configure & launch
    let state: AppStateExtension = Arc::new(Mutex::new(AppState { config, manager }));
    let app = Router::new()
        .route("/", get(routes::misc::index))
        .route("/archive", post(routes::archive::create))
        .route("/archive/:archive_id", get(routes::archive::get_meta))
        .route("/archive/:archive_id/videos", get(routes::archive::get_videos))
        .route("/archive/:archive_id", delete(routes::archive::delete))
        .route(
            "/archive/:archive_id/image/:image_hash/file",
            get(routes::image::get_file),
        )
        .route(
            "/archive/:archive_id/video/:video_id",
            get(routes::video::get),
        )
        .route(
            "/archive/:archive_id/video/:video_id/file",
            get(routes::video::get_file),
        )
        .route(
            "/archive/:archive_id/video/:video_id/note",
            post(routes::note::create),
        )
        .route(
            "/archive/:archive_id/video/:video_id/note/:note_id",
            patch(routes::note::update),
        )
        .route(
            "/archive/:archive_id/video/:video_id/note/:note_id",
            delete(routes::note::delete),
        )
        .with_state(state)
        .layer(CorsLayer::permissive());
    Ok(Server::bind(&addr).serve(app.into_make_service()).await?)
}

/// Gets or creates a new [Manager] from `manager_path` provided
fn get_manager(manager_path: PathBuf) -> Result<Manager> {
    match Manager::load(manager_path.clone()) {
        Ok(manager) => Ok(manager),
        Err(yark_archive::errors::Error::ManagerNotFound) => {
            log::info!(
                "Creating new manager file at {:?} as it doesn't exist",
                manager_path
            );
            let manager = Manager::new(manager_path);
            manager.save()?;
            Ok(manager)
        }
        Err(err) => Err(Error::Archive(err)),
    }
}
