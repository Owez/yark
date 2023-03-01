# from yark.archiver.converter import Converter
# from pathlib import Path
# c = Converter(Path("../demo/videos"))
# c.run()

from yark.archiver.archive import Archive
from yark.archiver.config import Config
from pathlib import Path

archive = Archive(
    Path("demo"), "https://www.youtube.com/channel/UCSMdm6bUYIBN0KfS2CVuEPA"
)
archive.commit()
md = archive.metadata_download(Config())
archive.metadata_parse(Config(), md)
archive.commit()
