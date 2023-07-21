//! Reporting extension for an archive enabling recommended report focuses based on a high amount of changed items in a given timescale

// NOTE: this could be in the archive core but i think it's best for it to be placed here as its a custom algo

use serde::Serialize;
use yark_archive::prelude::*;

type Reports<'a> = Vec<VideoReport<'a>>;

#[derive(Debug, PartialEq, Eq, Clone, Serialize)]
pub struct Report<'a> {
    pub videos: Reports<'a>,
    pub livestreams: Reports<'a>,
    pub shorts: Reports<'a>,
}

impl<'a> From<&Archive> for Report<'a> {
    fn from(value: &Archive) -> Self {
        Self {
            videos: Self::generate_reports(&value.videos),
            livestreams: Self::generate_reports(&value.livestreams),
            shorts: Self::generate_reports(&value.shorts),
        }
    }
}

impl<'a> Report<'a> {
    fn generate_reports(videos: &Videos) -> Reports<'a> {
        let mut reports = Vec::new();
        for video in videos.values() {
            let report = VideoReport::generate(video);
            if report.is_interesting() {
                reports.push(report);
            }
        }
        reports
    }
}

#[derive(Debug, PartialEq, Eq, Clone, Serialize)]
pub struct VideoReport<'a> {
    #[serde(skip_serializing)]
    pub video: &'a Video,
    pub title: ReportFocus,
    pub description: ReportFocus,
}

impl<'a> VideoReport<'a> {
    fn generate(video: &Video) -> Self {
        todo!()
    }

    fn is_interesting(&self) -> bool {
        self.title != ReportFocus::None && self.description != ReportFocus::None
    }
}

#[derive(Debug, PartialEq, Eq, Clone, Serialize)]
pub enum ReportFocus {
    None,
    Today(usize),
    ThisWeek(usize),
    ThisMonth(usize),
    ThisYear(usize),
}
