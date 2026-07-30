"""Tests for archive discovery on the filesystem."""

import tempfile
from pathlib import Path
from yark.web.routes import _discover_archives


class TestDiscoverArchives:
    def test_finds_single_archive(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "my-channel").mkdir()
            (root / "my-channel" / "yark.json").write_text("{}")
            (root / "unrelated").mkdir()

            found = _discover_archives(root)
            assert "my-channel" in found

    def test_finds_nested_archive(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            nested = root / "archives" / "cool-channel"
            nested.mkdir(parents=True)
            (nested / "yark.json").write_text("{}")

            found = _discover_archives(root)
            assert "archives/cool-channel" in found

    def test_empty_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            found = _discover_archives(Path(tmp))
            assert found == []

    def test_skips_hidden_dirs(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".git").mkdir()
            (root / ".git" / "yark.json").write_text("{}")
            (root / "__pycache__").mkdir()
            (root / "__pycache__" / "yark.json").write_text("{}")

            found = _discover_archives(root)
            # Neither .git nor __pycache__ should show up
            assert all(".git" not in f for f in found)
            assert all("__pycache__" not in f for f in found)

    def test_current_directory_archive(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "yark.json").write_text("{}")
            found = _discover_archives(root)
            assert "." in found

    def test_results_are_sorted(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for name in ["z-channel", "a-channel", "m-channel"]:
                (root / name).mkdir()
                (root / name / "yark.json").write_text("{}")

            found = _discover_archives(root)
            assert found == sorted(found)

    def test_respects_max_depth(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            deep = root / "a" / "b" / "c" / "d"
            deep.mkdir(parents=True)
            (deep / "yark.json").write_text("{}")

            found = _discover_archives(root, max_depth=2)
            assert found == []
