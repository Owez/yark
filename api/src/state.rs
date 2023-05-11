//! Configuration and state logic/utilities; see [Config]/[AppState] for more info

use crate::errors::{Error, Result};
use log::debug;
use std::{env, net::SocketAddr, path::PathBuf, str::FromStr, sync::Arc};
use tokio::sync::Mutex;
use yark_archive::prelude::*;

/// Configuration context for the API
pub struct Config {
    /// Host address
    pub host: String,
    /// Port number
    pub port: u32,
    /// Admin secret for extended operations
    pub admin_secret: String,
    /// Path to the permanent [Manager](yark_archive::manager::Manager) file
    pub manager_path: PathBuf,
}

impl Config {
    /// Generates a new config from [env::var] if valid
    pub fn from_vars() -> Result<Self> {
        debug!("Collecting configuration information");
        Ok(Self {
            host: get_var("HOST")?,
            port: get_var("PORT")?,
            admin_secret: get_var("ADMIN_SECRET")?,
            manager_path: get_var("MANAGER_PATH")?,
        })
    }

    /// Converts host and port to a usable socket address
    pub fn to_addr(&self) -> Result<SocketAddr> {
        let addr_str = format!("{}:{}", self.host, self.port);
        Ok(addr_str.parse()?)
    }
}

/// Gets environment variable from root `name` provided
fn get_var<T: FromStr>(name: &str) -> Result<T> {
    let var = env::var(gen_env_var_name(name))
        .map_err(|_| Error::EnvVarMissing(gen_env_var_name(name)))?;
    var.parse()
        .map_err(|_| Error::EnvVarInvalid(gen_env_var_name(name)))
}

/// Gets environment variable's name from root `name` provided
fn gen_env_var_name(name: &str) -> String {
    format!("YARK_{}", name)
}

pub struct AppState {
    pub config: Config,
    pub manager: Manager,
}

pub type AppStateExtension = Arc<Mutex<AppState>>;
