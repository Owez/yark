use std::net::AddrParseError;

pub type Result<T> = std::result::Result<T, Error>;

#[derive(Debug)]
pub enum Error {
    /// Environment variable is required but missing
    EnvVarMissing(String),
    /// Environment variable's type was invalid
    EnvVarInvalid(String),
    /// Invalid socket address for binding
    InvalidAddress(AddrParseError),
}
