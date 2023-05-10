//! Contains the [Error] and [Result] enum/type for easy management

use crate::state::AppState;
use axum::http::StatusCode;
use axum::response::IntoResponse;
use std::fmt;
use std::net::AddrParseError;
use std::sync::{MutexGuard, PoisonError};

/// Type cover for results based in this crate
pub type Result<T> = std::result::Result<T, Error>;

/// Enumeration for all of the possible errors during runtime
#[derive(Debug)]
pub enum Error {
    /// Environment variable is required but missing
    EnvVarMissing(String),
    /// Environment variable's type was invalid
    EnvVarInvalid(String),
    /// Invalid socket address for binding
    InvalidAddress(AddrParseError),
    /// Error during core archive management
    Archive(yark_archive::errors::Error),
    /// Internal actual hyper server error, out of our control
    Server(hyper::Error),
    /// Poison issue on a mutex lock for [AppState]
    StatePoison,
    /// Couldn't find archive during query
    ArchiveNotFound,
}

impl Error {
    /// Returns the status code
    fn status(&self) -> StatusCode {
        match self {
            Self::EnvVarMissing(_)
            | Self::EnvVarInvalid(_)
            | Self::InvalidAddress(_)
            | Self::Archive(_)
            | Self::Server(_)
            | Self::StatePoison => StatusCode::INTERNAL_SERVER_ERROR,
            Self::ArchiveNotFound => StatusCode::NOT_FOUND,
        }
    }
}

impl fmt::Display for Error {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Self::EnvVarMissing(var) => write!(f, "missing '{}' environment variable", var),
            Self::EnvVarInvalid(var) => write!(f, "invalid '{}' environment variable", var),
            Self::InvalidAddress(_) => write!(f, "invalid host/port address provided"),
            Self::Archive(err) => write!(f, "archive error, {}", err),
            Self::Server(err) => write!(f, "hyper server error we can't control, {}", err),
            Self::StatePoison => {
                write!(f, "poison on a mutex lock for the app state")
            }
            Self::ArchiveNotFound => write!(f, "couldn't find queried archive"),
        }
    }
}

impl IntoResponse for Error {
    fn into_response(self) -> axum::response::Response {
        (self.status(), format!("{}", self)).into_response()
    }
}

impl From<AddrParseError> for Error {
    fn from(err: AddrParseError) -> Self {
        Self::InvalidAddress(err)
    }
}

impl From<yark_archive::errors::Error> for Error {
    fn from(err: yark_archive::errors::Error) -> Self {
        Self::Archive(err)
    }
}

impl From<hyper::Error> for Error {
    fn from(err: hyper::Error) -> Self {
        Self::Server(err)
    }
}

impl From<PoisonError<MutexGuard<'_, AppState>>> for Error {
    fn from(_: PoisonError<MutexGuard<'_, AppState>>) -> Self {
        Self::StatePoison
    }
}
