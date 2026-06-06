"""Command-line interface for Yark."""

from __future__ import annotations

import sys
import threading
import webbrowser
from datetime import datetime
from pathlib import Path
from typing import Callable

from .core import Channel, DownloadConfig
from .core.channel import DownloadFilter, DownloadSelection
from .errors import ArchiveNotFoundException
from .terminal import ui
from .web.app import create_app

VERSION = "1.2.13"


def _cli() -> None:
    """Command-line launcher."""
    args = sys.argv[1:]
    if len(args) == 0:
        ui.help("Yark", _help_text())
        ui.error("No arguments provided")
        sys.exit(1)

    command = args[0]
    handlers: dict[str, Callable[[list[str]], None]] = {
        "new": _command_new,
        "refresh": _command_refresh,
        "view": _command_view,
        "report": _command_report,
    }

    if command in ["help", "--help", "-h"]:
        if len(args) > 1:
            ui.help(f"yark {args[1]}", _help_for_command(args[1]))
        else:
            ui.help("Yark", _help_text())
        return
    if command in ["-v", "-ver", "--version", "--v"]:
        ui.info(f"Yark {VERSION}")
        return

    handler = handlers.get(command)
    if handler is None:
        ui.help("Yark", _help_text())
        ui.error(f"Unknown command '{command}' provided", True)
        sys.exit(1)

    handler(args[1:])


def _command_new(args: list[str]) -> None:
    if len(args) == 1 and args[0] == "--help":
        ui.help("yark new", _help_for_command("new"))
        return
    if len(args) < 2:
        ui.error("Please provide an archive name and the channel URL")
        sys.exit(1)
    if len(args) > 2:
        ui.error(f"Unknown new option '{args[2]}'")
        sys.exit(1)
    Channel.new(Path(args[0]), args[1])


def _command_refresh(args: list[str]) -> None:
    if len(args) == 1 and args[0] == "--help":
        ui.help("yark refresh", _help_for_command("refresh"))
        return
    if len(args) < 1:
        ui.error("Please provide the archive name")
        sys.exit(1)

    config = _parse_refresh_config(args[1:])
    try:
        config.submit()
    except ValueError as error:
        ui.error(str(error))
        sys.exit(1)

    try:
        channel = Channel.load(args[0])
        channel.verbose = config.verbose
        channel.configure_cookies_file()
        if config.verbose:
            ui.info(f"Verbose mode enabled for archive '{args[0]}'")
        if config.skip_metadata:
            ui.warning("Skipping metadata download")
        else:
            channel.metadata()
        if config.skip_download:
            ui.warning("Skipping videos/livestreams/shorts download")
        else:
            channel.download(config)
        channel.commit()
        channel.reporter.print()
    except ArchiveNotFoundException:
        _err_archive_not_found()


def _parse_refresh_config(config_args: list[str]) -> DownloadConfig:
    config = DownloadConfig()

    def parse_value(flag: str) -> str:
        if "=" in flag:
            return flag.split("=", 1)[1]
        raise ValueError(f"No value provided for {flag}")

    def parse_maximum(flag: str) -> int:
        value = parse_value(flag)
        try:
            return int(value)
        except ValueError:
            raise ValueError(f"The value '{value}' isn't a valid maximum number")

    def parse_date(flag: str) -> datetime:
        value = parse_value(flag).strip()
        for fmt in ["%Y-%m-%d", "%Y%m%d"]:
            try:
                return datetime.strptime(value, fmt)
            except ValueError:
                continue
        raise ValueError(
            f"The value '{value}' isn't a valid date, use YYYY-MM-DD or YYYYMMDD"
        )

    def parse_selection(flag: str) -> DownloadSelection:
        value = parse_value(flag)
        if ":" not in value:
            return DownloadSelection(maximum=parse_maximum(flag))

        raw_filter, raw_maximum = value.split(":", 1)
        normalized_filter = raw_filter.strip().lower().replace("most-", "")
        filter_map = {
            "recent": DownloadFilter.RECENT,
            "popular": DownloadFilter.POPULAR,
        }
        selected_filter = filter_map.get(normalized_filter)
        if selected_filter is None:
            raise ValueError(
                f"Unknown download filter '{raw_filter}'. Use recent or popular"
            )

        try:
            maximum = int(raw_maximum)
        except ValueError:
            raise ValueError(f"The value '{raw_maximum}' isn't a valid maximum number")
        return DownloadSelection(maximum=maximum, filter=selected_filter)

    for config_arg in config_args:
        try:
            if config_arg.startswith("--videos="):
                config.videos = parse_selection(config_arg)
            elif config_arg.startswith("--livestreams="):
                config.livestreams = parse_selection(config_arg)
            elif config_arg.startswith("--shorts="):
                config.shorts = parse_selection(config_arg)
            elif config_arg == "--skip-metadata":
                config.skip_metadata = True
            elif config_arg == "--skip-download":
                config.skip_download = True
            elif config_arg == "--verbose":
                config.verbose = True
            elif config_arg.startswith("--format="):
                config.format = parse_value(config_arg)
            elif config_arg.startswith("--date-min="):
                config.uploaded_after = parse_date(config_arg)
            elif config_arg.startswith("--date-max="):
                config.uploaded_before = parse_date(config_arg)
            else:
                ui.error(f"Unknown refresh option '{config_arg}'")
                sys.exit(1)
        except ValueError as error:
            ui.error(str(error))
            sys.exit(1)

    return config


def _command_view(args: list[str]) -> None:
    if len(args) == 1 and args[0] == "--help":
        ui.help("yark view", _help_for_command("view"))
        return

    archive_name = args[0] if len(args) > 0 and not args[0].startswith("--") else None
    config_args = args[1:] if archive_name is not None else args
    host, port = _parse_view_config(config_args)

    if archive_name is not None and not Path(archive_name).exists():
        _err_archive_not_found()

    def launch() -> None:
        app = create_app()
        threading.Thread(target=lambda: app.run(host=host, port=port)).run()

    if archive_name is not None:
        url = f"http://127.0.0.1:{port}/channel/{archive_name}/videos"
        ui.info(f"Starting viewer for {archive_name}")
    else:
        url = f"http://127.0.0.1:{port}/"
        ui.info("Starting viewer")

    webbrowser.open(url)
    launch()


def _parse_view_config(config_args: list[str]) -> tuple[str | None, int]:
    host = None
    port = 7667
    for config_arg in config_args:
        if config_arg.startswith("--host="):
            host = config_arg.split("=", 1)[1]
        elif config_arg.startswith("--port="):
            raw = config_arg.split("=", 1)[1].strip()
            if raw == "":
                ui.error("No port number provided for --port")
                sys.exit(1)
            try:
                port = int(raw)
            except ValueError:
                ui.error(f"Invalid port number '{raw}' provided")
                sys.exit(1)
        else:
            ui.error(f"Unknown view option '{config_arg}'")
            sys.exit(1)
    return host, port


def _command_report(args: list[str]) -> None:
    if len(args) == 1 and args[0] == "--help":
        ui.help("yark report", _help_for_command("report"))
        return
    if len(args) < 1:
        ui.error("Please provide the archive name")
        sys.exit(1)
    channel = Channel.load(Path(args[0]))
    channel.reporter.interesting_changes()


def _err_archive_not_found():
    """Errors out the user if the archive doesn't exist"""
    ui.error("Archive doesn't exist, please make sure you typed its name correctly!")
    sys.exit(1)


def _help_text() -> str:
    return (
        "yark [options]\n\n"
        "YouTube archiving made simple.\n\n"
        "Commands:\n"
        "  new [name] [url] Create a new archive\n"
        "  refresh [name] [args?] Refresh/download archive\n"
        "  view [name?] [args?] Launch offline archive viewer\n"
        "  report [name] Show interesting changes\n\n"
        "Examples:\n"
        "  yark new demo https://www.youtube.com/channel/...\n"
        "  yark refresh demo --videos=5\n"
        "  yark view demo --port=8080"
    )


def _help_for_command(command: str) -> str:
    docs = {
        "new": (
            "yark new [name] [url]\n\n"
            "Creates a new archive from a YouTube URL.\n\n"
            "Arguments:\n"
            "  (no optional arguments)"
        ),
        "refresh": (
            "yark refresh [name] [args?]\n\n"
            "Refreshes/downloads archive with optional configuration.\n\n"
            "Arguments:\n"
            "  --videos=[max|filter:max]        Download video selection\n"
            "  --shorts=[max|filter:max]        Download shorts selection\n"
            "  --livestreams=[max|filter:max]   Download livestream selection\n"
            "  --date-min=[YYYY-MM-DD]          Only download uploads on/after date\n"
            "  --date-max=[YYYY-MM-DD]          Only download uploads on/before date\n"
            "  --verbose                        Print detailed refresh diagnostics\n"
            "  --skip-metadata       Skip metadata download\n"
            "  --skip-download       Skip media download\n"
            "  --format=[str]        Custom yt-dlp format\n\n"
            "Filters:\n"
            "  recent   Most recent entries (default)\n"
            "  popular  Highest view count entries\n\n"
            "Examples:\n"
            "  --videos=5\n"
            "  --videos=recent:5\n"
            "  --videos=popular:10\n"
            "  --date-min=2025-01-01 --date-max=2025-12-31\n"
            "  --verbose"
        ),
        "view": (
            "yark view [name] [args?]\n\n"
            "Launches the offline archive viewer website.\n\n"
            "Arguments:\n"
            "  --host=[str]   Custom host\n"
            "  --port=[int]   Custom port (default 7667)"
        ),
        "report": "yark report [name]\n\nPrints interesting archive changes.",
    }
    return docs.get(command, "No additional help for this command.")


def main():
    """Primary console entrypoint."""
    _cli()
