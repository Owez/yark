use serde::{Deserialize, Serialize};
use uuid::Uuid;

#[derive(Debug, PartialEq, Clone, Serialize, Deserialize)]
pub struct Note {
    pub id: Uuid,
    pub timestamp: u32,
    pub title: String,
    pub description: String,
}

impl Note {
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
    fn timestamp_to_str() {
        let note = Note {
            id: Uuid::new_v4(),
            timestamp: 65,
            title: "Test Note".to_string(),
            description: "This is a test note".to_string(),
        };
        assert_eq!(note.to_timestamp_str(), "01:05");

        let note = Note {
            id: Uuid::new_v4(),
            timestamp: 3750,
            title: "Test Note".to_string(),
            description: "This is a test note".to_string(),
        };
        assert_eq!(note.to_timestamp_str(), "01:02:30");
    }

    #[test]
    fn note_serialization() {
        let note = Note {
            id: Uuid::new_v4(),
            timestamp: 120,
            title: "Test Note".to_string(),
            description: "This is a test note".to_string(),
        };
        let serialized_note = serde_json::to_string(&note).unwrap();
        let deserialized_note: Note = serde_json::from_str(&serialized_note).unwrap();
        assert_eq!(note, deserialized_note);
    }
}
