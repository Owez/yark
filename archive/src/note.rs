use serde::{Deserialize, Serialize};
use uuid::Uuid;

#[derive(Debug, PartialEq, Clone, Serialize, Deserialize)]
pub struct Note {
    pub id: Uuid,
    pub timestamp: u32,
    pub title: String,
    pub description: String,
}
