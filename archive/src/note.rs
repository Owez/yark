//! Note/journalling logic; see [Note] for more info

use serde::{Deserialize, Serialize};
use uuid::Uuid;

/// User-written note for a video to comment on something at a specific time
#[derive(Debug, PartialEq, Clone, Serialize, Deserialize)]
pub struct Note {
    /// Unique queryable identifier of this note
    pub id: Uuid,
    /// Timestamp (in seconds) that this note refers to
    pub timestamp: u32,
    /// Title of this note which the user has wrote
    pub title: String,
    /// Optional description of this note with extra content; assumed to be plaintext
    #[deprecated(
        since = "3.1.0-beta.1",
        note = "Will be superseded in v4 by Note::body"
    )]
    pub description: Option<String>,
}

impl Note {
    /// Converts a [Self::timestamp] into a properly-formatted string for visual use
    ///
    /// If it's over an hour, it'll look like `12:05:21` and if it's under it'll be `05:21`.
    pub fn to_timestamp_str(&self) -> String {
        let mut mins = self.timestamp / 60;
        let secs = self.timestamp % 60;
        if mins > 60 {
            let hours = mins / 60;
            mins = mins % 60;
            format!("{:02}:{:02}:{:02}", hours, mins, secs)
        } else {
            format!("{:02}:{:02}", mins, secs)
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    #[allow(deprecated)]
    fn timestamp_to_str() {
        let note = Note {
            id: Uuid::new_v4(),
            timestamp: 65,
            title: "Test Note".to_string(),
            description: Some("This is a test note".to_string()),
        };
        assert_eq!(note.to_timestamp_str(), "01:05");

        let note = Note {
            id: Uuid::new_v4(),
            timestamp: 3750,
            title: "Test Note".to_string(),
            description: Some("This is a test note".to_string()),
        };
        assert_eq!(note.to_timestamp_str(), "01:02:30");
    }

    #[test]
    #[allow(deprecated)]
    fn note_serialization() {
        let note = Note {
            id: Uuid::new_v4(),
            timestamp: 120,
            title: "Test Note".to_string(),
            description: Some("This is a test note".to_string()),
        };
        let serialized_note = serde_json::to_string(&note).unwrap();
        let deserialized_note: Note = serde_json::from_str(&serialized_note).unwrap();
        assert_eq!(note, deserialized_note);
    }
}
