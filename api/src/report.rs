//! Reporting extension for an archive enabling recommended report focuses based on a high amount of changed items in a given timescale

use chrono::{prelude::*, TimeDelta};
use serde::Serialize;
use yark_archive::prelude::*;

type Reports = Vec<VideoReport>;

#[derive(Debug, PartialEq, Eq, Clone, Serialize)]
pub struct Report {
    pub videos: Reports,
    pub livestreams: Reports,
    pub shorts: Reports,
}

impl From<&Archive> for Report {
    fn from(value: &Archive) -> Self {
        Self {
            videos: Self::generate_reports(&value.videos),
            livestreams: Self::generate_reports(&value.livestreams),
            shorts: Self::generate_reports(&value.shorts),
        }
    }
}

impl Report {
    fn generate_reports(videos: &Videos) -> Reports {
        let mut reports = Vec::new();
        for video in videos.values() {
            let report = VideoReport::from(video);
            if report.is_interesting() {
                reports.push(report);
            }
        }
        reports
    }
}

#[derive(Debug, PartialEq, Eq, Clone, Serialize)]
pub struct VideoReport {
    pub video: Video,
    pub title: Option<ReportFocus>,
    pub description: Option<ReportFocus>,
}

impl From<&Video> for VideoReport {
    fn from(value: &Video) -> Self {
        Self {
            video: value.clone(),
            title: ReportFocus::from_elements(&value.title),
            description: ReportFocus::from_elements(&value.description),
        }
    }
}

impl VideoReport {
    fn is_interesting(&self) -> bool {
        self.title.is_some() || self.description.is_some()
    }
}

#[derive(Debug, PartialEq, Eq, Clone, Serialize)]
#[serde(rename_all = "snake_case")]
pub enum ReportFocus {
    Month(usize),
    Year(usize),
}

impl ReportFocus {
    fn from_elements<T>(value: &Elements<T>) -> Option<Self> {
        if value.len() < 2 {
            return None;
        }
        let now = Utc::now();
        let month_ago = now - TimeDelta::days(30);
        let year_ago = now - TimeDelta::days(365);
        let mut month_count = 0;
        let mut year_count = 0;
        for dt in value.0.keys() {
            if dt.0 >= month_ago {
                month_count += 1;
            }
            if dt.0 >= year_ago {
                year_count += 1;
            }
        }
        if month_count == 0 && year_count == 0 {
            None
        } else if year_count / 12 > month_count {
            Some(Self::Year(year_count))
        } else {
            Some(Self::Month(month_count))
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn more_than_year_ago() {
        let mut elements = Elements::new();
        let two_years_ago = Utc::now() - TimeDelta::days(365 * 2);
        elements.insert(two_years_ago, "hello!");
        let _ = ReportFocus::from_elements(&elements);
    }
}
