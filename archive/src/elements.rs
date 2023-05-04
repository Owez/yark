use chrono::prelude::*;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;

#[derive(Debug, PartialEq, Clone, Serialize, Deserialize)]
pub struct Elements<T>(pub HashMap<DateTime<Utc>, T>);

impl<T> Elements<T> {
    pub fn new_now(value: T) -> Self {
        let mut elements = Self::default();
        elements.insert_now(value);
        elements
    }

    pub fn insert_now(&mut self, value: T) {
        let now = Utc::now();
        self.insert(now, value)
    }

    pub fn insert(&mut self, date: DateTime<Utc>, value: T) {
        self.0.insert(date, value);
    }
}

impl<T> Default for Elements<T> {
    fn default() -> Self {
        Self(HashMap::default())
    }
}
