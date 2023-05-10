//! REST API for web-based Yark instances

pub mod errors;
pub mod routes;
pub mod state;

use crate::errors::Result;
use crate::state::Config;
use axum::routing::{get, post};
use axum::{Router, Server};
use log::info;
use state::AppState;
use std::fmt;
use std::process::exit;
use std::sync::{Arc, Mutex};
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
    // Get required preamble
    let config = Config::from_vars()?;
    let manager = Manager::load(config.manager_path.clone())?;
    let addr = config.to_addr()?;

    // Log to user
    info!(
        "Launching at http://{}:{} address",
        config.host, config.port
    );

    // Configure & launch
    let state = Arc::new(Mutex::new(AppState { config, manager }));
    let app = Router::new()
        .route("/", get(routes::misc::index))
        .route("/archive", post(routes::archive::create))
        .route("/archive/:archive_id", get(routes::archive::get))
        .with_state(state);
    Ok(Server::bind(&addr).serve(app.into_make_service()).await?)
}
