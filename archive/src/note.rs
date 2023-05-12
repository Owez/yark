//! Note/journalling logic; see [Note] for more info

use std::collections::HashMap;

use serde::{Deserialize, Serialize};
use uuid::Uuid;

/// User-written note for a video to comment on something at a specific time
#[derive(Debug, PartialEq, Eq, Clone, Serialize, Deserialize)]
pub struct Note {
    /// Unique queryable identifier of this note
    pub id: Uuid,
    /// Timestamp (in seconds) that this note refers to
    pub timestamp: u32,
    /// Title of this note which the user has wrote
    pub title: String,
    /// Optional description of this note with extra content; assumed to be plaintext
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

/// List of [Note] items which can be queried as a [HashMap]
#[derive(Debug, PartialEq, Eq, Clone)]

pub struct Notes(pub HashMap<Uuid, Note>);

impl Notes {
    pub fn get(&self, id: &Uuid) -> Option<&Note> {
        self.0.get(id)
    }

    pub fn get_mut(&mut self, id: &Uuid) -> Option<&mut Note> {
        self.0.get_mut(id)
    }

    pub fn insert(&mut self, note: Note) {
        self.0.insert(note.id.clone(), note);
    }

    pub fn remove(&mut self, id: &Uuid) -> Option<Note> {
        self.0.remove(id)
    }
}

impl Default for Notes {
    fn default() -> Self {
        Self(HashMap::default())
    }
}

impl Serialize for Notes {
    fn serialize<S>(&self, serializer: S) -> std::result::Result<S::Ok, S::Error>
    where
        S: serde::Serializer,
    {
        let vec = self.0.values().cloned().collect::<Vec<_>>();
        vec.serialize(serializer)
    }
}

impl<'de> Deserialize<'de> for Notes {
    fn deserialize<D>(deserializer: D) -> std::result::Result<Self, D::Error>
    where
        D: serde::Deserializer<'de>,
    {
        let vec = Vec::<Note>::deserialize(deserializer)?;
        let mut map = HashMap::new();
        for note in vec {
            map.insert(note.id.clone(), note);
        }
        Ok(Notes(map))
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
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
