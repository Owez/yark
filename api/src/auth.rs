//! Authentication provider for the API; see [check] for more info

use crate::{
    errors::{Error, Result},
    state::Config,
};
use axum_auth::AuthBearer;

/// Checks auth provided compared to the admin secret stored in config
pub fn check(config: &Config, AuthBearer(bearer): AuthBearer) -> Result<()> {
    if config.admin_secret == bearer {
        Ok(())
    } else {
        Err(Error::InvalidAdminSecret)
    }
}
