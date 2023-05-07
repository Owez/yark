use chrono::prelude::*;
use serde::{Deserialize, Deserializer, Serialize};

/// Wrapper around [DateTime]<[Utc]> due to varying serialization/deserialization
#[derive(Debug, PartialEq, Eq, PartialOrd, Ord, Clone, Serialize)]
pub struct YarkDate(pub DateTime<Utc>);

impl<'de> Deserialize<'de> for YarkDate {
    fn deserialize<D>(deserializer: D) -> std::result::Result<Self, D::Error>
    where
        D: Deserializer<'de>,
    {
        Ok(YarkDate(deserialize_date(deserializer)?))
    }
}

/// Deserializes a date produced from two possible sources
///
/// 1. Chrono: Automatically adds proper timezones, we can use this natively
/// 2. Python: Forgets to add UTC so we add a manual `+00:00` offset so [chrono] can parse
fn deserialize_date<'de, D: Deserializer<'de>>(
    deserializer: D,
) -> std::result::Result<DateTime<Utc>, D::Error> {
    let s: &str = Deserialize::deserialize(deserializer)?;
    let s_with_offset = if s.ends_with("Z") || s.ends_with("+00:00") {
        s.to_owned()
    } else {
        format!("{}+00:00", s)
    };
    DateTime::<Utc>::parse_from_rfc3339(&s_with_offset).map_err(serde::de::Error::custom)
}

impl From<DateTime<Utc>> for YarkDate {
    fn from(dt: DateTime<Utc>) -> Self {
        Self(dt)
    }
}

impl Into<DateTime<Utc>> for YarkDate {
    fn into(self) -> DateTime<Utc> {
        self.0
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use serde_json::json;

    #[test]
    fn deserialize_date() {
        let date_str = "2023-05-07T12:00:00Z";
        let expected_date = YarkDate(Utc.with_ymd_and_hms(2023, 5, 7, 12, 0, 0).unwrap());

        let result: YarkDate = serde_json::from_str(&json!(date_str).to_string()).unwrap();
        assert_eq!(result, expected_date);
    }

    #[test]
    fn deserialize_date_with_invalid_timezone() {
        let date_str = "2023-05-07T12:00:00+02:00";
        let expected_err = "trailing input";

        let result: Result<YarkDate, _> = serde_json::from_str(&json!(date_str).to_string());
        assert!(result.is_err());
        assert_eq!(result.unwrap_err().to_string(), expected_err);
    }

    #[test]
    fn deserialize_date_with_missing_timezone() {
        let date_str = "2023-05-07T12:00:00";
        let expected_date = YarkDate(Utc.with_ymd_and_hms(2023, 5, 7, 12, 0, 0).unwrap());

        let result: YarkDate = serde_json::from_str(&json!(date_str).to_string()).unwrap();
        assert_eq!(result, expected_date);
    }

    #[test]
    fn deserialize_with_invalid_date() {
        let date_str = "invalid-date-string";

        let result: Result<YarkDate, _> = serde_json::from_str(&json!(date_str).to_string());
        assert!(result.is_err());
    }
}
