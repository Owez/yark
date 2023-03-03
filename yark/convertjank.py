# from yark.archiver.converter import Converter
# from pathlib import Path
# c = Converter(Path("../demo/videos"))
# c.run()

from yark.archiver.archive import Archive
from yark.archiver.video.note import Note
from pathlib import Path

archive = Archive.load(Path("../demo"))
video = archive.videos.inner["Jlsxl-1zQJM"]
video.notes.append(Note(video, 1, "My example note", "This is the note's body"))
video.notes.append(Note(video, 60, "Second note", "This is the second note's body"))
archive.commit()
