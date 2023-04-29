# Standard Imports
import pickle
import unittest

# Local Imports
import tests.archive

# External Imports
from yark.yark.archiving.config.data import Config
from yark.yark.archiving.archiver import download
from yark.yark.archiving.archive.data.video import comment


class CommentAuthorTestCase(unittest.TestCase):

    def test_load(self):
        config = Config()

        if not tests.archive.temp_raw_metadata_path.exists():
            tests.archive.temp_raw_metadata_path.parent.mkdir(parents=True, exist_ok=True)

            raw_metadata = download.metadata_download(tests.archive.channel_url, config)

            with tests.archive.temp_raw_metadata_path.open('wb') as f:
                pickle.dump(raw_metadata, f)
        else:
            with tests.archive.temp_raw_metadata_path.open('rb') as f:
                raw_metadata = pickle.load(f)

        video_data = raw_metadata['entries'][0]
        for comment_dict in raw_metadata['']:
            some_comment = comment._from_archive_ib(comment_dict)


