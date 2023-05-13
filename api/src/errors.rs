//! Contains the [Error] and [Result] enum/type for easy management

use axum::http::StatusCode;
use axum::response::{IntoResponse, Response};
use std::net::AddrParseError;
use std::{fmt, io};

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
    /// Couldn't find archive during query
    ArchiveNotFound,
    /// Couldn't find video in archive during query
    VideoNotFound,
    /// Couldn't find image in archive during query
    ImageNotFound,
    /// Couldn't find note in archive during query
    NoteNotFound,
    /// Failed to share a file in a response
    FileShare(io::Error),
    /// Admin secret shared was invalid
    InvalidAdminSecret,
    /// Directory path provided couldn't be queried due to fs error
    DirectoryPath(io::Error),
    /// Couldn't find directory during query
    DirectoryNotFound,
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
            | Self::FileShare(_)
            | Self::DirectoryPath(_) => StatusCode::INTERNAL_SERVER_ERROR,
            Self::ArchiveNotFound
            | Self::VideoNotFound
            | Self::ImageNotFound
            | Self::NoteNotFound
            | Self::DirectoryNotFound => StatusCode::NOT_FOUND,
            Self::InvalidAdminSecret => StatusCode::UNAUTHORIZED,
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
            Self::ArchiveNotFound => write!(f, "couldn't find queried archive"),
            Self::VideoNotFound => write!(f, "couldn't find queried video"),
            Self::ImageNotFound => write!(f, "couldn't find queried image"),
            Self::NoteNotFound => write!(f, "couldn't find queried note"),
            Self::FileShare(err) => write!(f, "failed to share a file with user, {}", err),
            Self::InvalidAdminSecret => write!(f, "invalid admin secret provided"),
            Self::DirectoryPath(err) => {
                write!(f, "path to directory to query had an issue, {}", err)
            }
            Self::DirectoryNotFound => write!(f, "couldn't find queried directory"),
        }
    }
}

impl IntoResponse for Error {
    fn into_response(self) -> Response {
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
