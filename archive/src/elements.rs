use chrono::prelude::*;
use serde::{Deserialize, Serialize};
use std::collections::BTreeMap;

use crate::date::YarkDate;

#[derive(Debug, PartialEq, Clone, Serialize, Deserialize)]
pub struct Elements<T>(pub BTreeMap<YarkDate, T>);

impl<T> Elements<T> {
    pub fn new_now(value: T) -> Self {
        let mut elements = Self::default();
        elements.insert_now(value);
        elements
    }

    pub fn new_existing(dt: impl Into<YarkDate>, value: T) -> Self {
        let mut elements = Elements::default();
        elements.insert(dt, value);
        elements
    }

    pub fn insert_now(&mut self, value: T) {
        let now = Utc::now();
        self.insert(now, value)
    }

    pub fn insert(&mut self, dt: impl Into<YarkDate>, value: T) {
        self.0.insert(dt.into(), value);
    }

    pub fn current(&self) -> Option<&T> {
        self.0.values().next_back()
    }
}

impl<T> Default for Elements<T> {
    fn default() -> Self {
        Self(BTreeMap::default())
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_most_recent_value_empty() {
        let elements: Elements<i32> = Elements::default();
        assert_eq!(elements.current(), None);
    }

    #[test]
    fn test_most_recent_value() {
        let mut elements = Elements::default();
        elements.0.insert(
            YarkDate(DateTime::<Utc>::from_utc(
                NaiveDateTime::from_timestamp_opt(1, 0).unwrap(),
                Utc,
            )),
            1,
        );
        elements.0.insert(
            YarkDate(DateTime::<Utc>::from_utc(
                NaiveDateTime::from_timestamp_opt(2, 0).unwrap(),
                Utc,
            )),
            2,
        );
        elements.0.insert(
            YarkDate(DateTime::<Utc>::from_utc(
                NaiveDateTime::from_timestamp_opt(3, 0).unwrap(),
                Utc,
            )),
            3,
        );
        assert_eq!(elements.current(), Some(&3));
    }
}
