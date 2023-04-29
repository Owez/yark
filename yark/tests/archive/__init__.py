# Standard Imports
from pathlib import Path

# Local Imports
import tests

# External Imports


archive_path = Path(f'{tests.__path__[0]}/archives/')
# channel_url = 'https://www.youtube.com/channel/UCSMdm6bUYIBN0KfS2CVuEPA'
channel_url = 'https://www.youtube.com/@milliesilva934/'

temp_data_path = Path(f'{tests.__path__[0]}/_data_/temp/')
temp_raw_metadata_path = Path(f'{tests.__path__[0]}/_data_/temp/raw_metadata.pkl')


def clean_temp_data():
    Path(f'{tests.__path__[0]}/_data_/temp').unlink()

