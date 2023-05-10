//! REST API for web-based Yark instances

pub mod config;
pub mod errors;
pub mod routes;

use crate::config::Config;
use crate::errors::{Error, Result};
use axum::routing::get;
use axum::{Router, Server};
use std::fmt;
use std::process::exit;

#[tokio::main]
async fn main() {
    match launch().await {
        Ok(()) => (),
        Err(Error::EnvVarMissing(var)) => {
            err_exit(format!("Missing '{}' environment variable", var))
        }
        Err(Error::EnvVarInvalid(var)) => {
            err_exit(format!("Invalid '{}' environment variable", var))
        }
        Err(Error::InvalidAddress(_)) => err_exit("Invalid address provided for host/port"),
    }
}

/// Exits program with fatal error message
fn err_exit(msg: impl fmt::Display) -> ! {
    eprintln!("Fatal error: {}", msg);
    exit(1)
}

/// Launches axum web server or fatally errors during the process
async fn launch() -> Result<()> {
    let config = Config::from_vars()?;
    let app = Router::new().route("/", get(routes::misc::index));
    Server::bind(&config.to_addr()?).serve(app.into_make_service());
    Ok(())
}
