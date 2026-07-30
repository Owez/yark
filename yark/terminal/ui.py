"""Centralized terminal UI helpers built on Rich."""

from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator

from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table


class TerminalUI:
    """Small facade for consistent CLI output formatting."""

    def __init__(self) -> None:
        self.console = Console()
        self.error_console = Console(stderr=True)

    def info(self, message: str) -> None:
        self.console.print(f"[cyan]•[/cyan] {message}")

    def success(self, message: str) -> None:
        self.console.print(f"[green]✓[/green] {message}")

    def warning(self, message: str) -> None:
        self.error_console.print(f"[yellow]![/yellow] {message}")

    def error(self, message: str, report_msg: bool = False) -> None:
        suffix = (
            "\nPlease file a bug report if you think this is a problem with Yark!"
            if report_msg
            else ""
        )
        self.error_console.print(f"[bold red]{message}{suffix}[/bold red]")

    def plain(self, message: str = "") -> None:
        self.console.print(message)

    def help(self, title: str, body: str) -> None:
        self.console.print(
            Panel(body, title=title, border_style="cyan", box=box.ROUNDED)
        )

    @contextmanager
    def status(self, message: str) -> Iterator[None]:
        with self.console.status(f"[bold cyan]{message}"):
            yield

    def render_change_report(
        self,
        channel_name: str,
        updated: list[tuple[str, str]],
        added: list[str],
        deleted: list[str],
        watermark: str,
    ) -> None:
        self.console.print(
            Panel(
                f"Archive report for [bold]{channel_name}[/bold]",
                border_style="cyan",
                box=box.ROUNDED,
            )
        )

        table = Table(box=box.ROUNDED, show_header=True, header_style="bold cyan",
                      width=100)
        table.add_column("Type", width=10)
        table.add_column("Video", overflow="fold", max_width=54)
        table.add_column("Change", overflow="fold", max_width=24)

        for kind, video in updated:
            style = "cyan" if kind in ["title", "description", "undeleted"] else "blue"
            table.add_row("Updated", video, f"[{style}]{kind.capitalize()}[/{style}]")
        for video in added:
            table.add_row("Added", f"[green]{video}[/green]", "")
        for video in deleted:
            table.add_row("Deleted", f"[red]{video}[/red]", "")

        if len(table.rows) == 0:
            self.console.print(
                Panel(
                    "No videos were added, updated, or deleted.",
                    border_style="dim",
                    box=box.ROUNDED,
                )
            )
        else:
            self.console.print(table)

        self.console.print(f"[dim]{watermark}[/dim]")

    def render_interesting_section(self, kind: str, rows: list[tuple[str, str, str]]) -> None:
        table = Table(
            title=f"Interesting {kind}",
            box=box.ROUNDED,
            show_header=True,
            header_style="bold cyan",
        )
        table.add_column("Title", overflow="fold")
        table.add_column("Changes", overflow="fold")
        table.add_column("Viewer URL", overflow="fold")

        for title, changes, url in rows:
            table.add_row(title, changes, url)

        self.console.print(table)

    def render_empty_interesting(self, empty_kinds: list[str]) -> None:
        joined = "/".join(empty_kinds)
        self.console.print(f"[dim]No interesting {joined} found[/dim]")


ui = TerminalUI()