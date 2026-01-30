"""Main splitting logic for CUE sheets."""

from __future__ import annotations

from typing import TYPE_CHECKING

from rich.console import Console
from rich.panel import Panel
from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn
from rich.table import Table

from .audio import ffprobe_duration_seconds, run_ffmpeg_extract_to_alac, safe_filename
from .cue_parser import parse_cue

if TYPE_CHECKING:
    from pathlib import Path

console = Console()


class CueSplitter:
    """Splits audio based on CUE sheet into individual ALAC tracks."""

    def __init__(  # noqa: PLR0913, PLR0917
        self,
        audio: Path,
        cue: Path,
        cover: Path | None = None,
        album_override: str = "",
        album_artist_override: str = "",
        date_override: str = "",
        genre_override: str = "",
    ) -> None:
        """
        Initialize splitter with source files and metadata overrides.

        Args:
            audio (Path): Input audio file.
            cue (Path): CUE sheet file.
            cover (Path | None): Cover image file (optional).
            album_override (str): Override album title.
            album_artist_override (str): Override album artist.
            date_override (str): Override date/year.
            genre_override (str): Override genre.

        Raises:
            FileNotFoundError: If required files don't exist.

        """
        if not audio.exists():
            raise FileNotFoundError(audio)
        if not cue.exists():
            raise FileNotFoundError(cue)
        if cover is not None and not cover.exists():
            raise FileNotFoundError(cover)

        self.audio = audio
        self.cue = cue
        self.cover = cover
        self.album_override = album_override
        self.album_artist_override = album_artist_override
        self.date_override = date_override
        self.genre_override = genre_override

    def split(self, outdir: Path, *, dry_run: bool = False) -> None:  # noqa: PLR0914
        """
        Split audio file based on CUE sheet and save ALAC tracks.

        Args:
            outdir (Path): Output directory for ALAC files.
            dry_run (bool): If True, print commands without executing.

        """
        cue_info = parse_cue(self.cue)

        album_title = self.album_override or cue_info.album or "Unknown Album"
        album_artist_name = (
            self.album_artist_override or cue_info.album_artist or "Unknown Artist"
        )
        date_val = self.date_override or cue_info.date
        genre_val = self.genre_override or cue_info.genre

        full_dur = ffprobe_duration_seconds(self.audio)

        outdir.mkdir(parents=True, exist_ok=True)

        tracks = cue_info.tracks
        total = len(tracks)

        # Display album info
        _display_album_info(album_title, album_artist_name, total, dry_run=dry_run)

        # Build (start, duration) per track
        with Progress(
            SpinnerColumn(),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TextColumn("•"),
            TextColumn("[cyan]{task.fields[status]}"),
            console=console,
        ) as progress:
            task_id = progress.add_task("[cyan]Converting...", total=total, status="")

            for idx, tr in enumerate(tracks, start=1):
                start = float(tr.index01_seconds or 0.0)
                if idx < total:
                    next_start = float(tracks[idx].index01_seconds or full_dur)
                    dur = max(0.0, next_start - start)
                else:
                    dur = max(0.0, full_dur - start)

                title = tr.title or f"Track {tr.number:02d}"
                artist = tr.performer or album_artist_name

                out_name = f"{idx:02d} - {safe_filename(title)}.m4a"
                out_path = outdir / out_name

                # Update progress with current track info
                progress.update(
                    task_id,
                    status=f"[{idx:02d}/{total:02d}] {title}",
                )

                run_ffmpeg_extract_to_alac(
                    audio=self.audio,
                    cover=self.cover,
                    out_file=out_path,
                    start=start,
                    duration=dur,
                    album=album_title,
                    album_artist=album_artist_name,
                    artist=artist,
                    title=title,
                    track_num=idx,
                    track_total=total,
                    date=date_val,
                    genre=genre_val,
                    dry_run=dry_run,
                )

                progress.advance(task_id)

        # Display completion message
        _display_completion(total, outdir, dry_run=dry_run)


def _display_album_info(
    album_title: str,
    album_artist: str,
    total_tracks: int,
    *,
    dry_run: bool,
) -> None:
    """Показать информацию об альбоме в красивом формате."""
    table = Table(title="Album Info", show_header=False, box=None)
    table.add_row("Album:", album_title)
    table.add_row("Artist:", album_artist)
    table.add_row("Tracks:", str(total_tracks))
    if dry_run:
        table.add_row("Mode:", "[yellow]DRY RUN[/yellow]")

    console.print(table)
    console.print()


def _display_completion(
    total_tracks: int,
    outdir: Path,
    *,
    dry_run: bool,
) -> None:
    """Показать сообщение о завершении."""
    message: str = ""
    if dry_run:
        message = (
            f"[yellow]Dry run completed[/yellow] — {total_tracks} "
            "tracks would be converted"
        )
    else:
        message = (
            f"[green]✓ Conversion completed![/green] "
            f"[cyan]{total_tracks} tracks[/cyan] saved to "
            f"[blue]{outdir}[/blue]"
        )

    panel = Panel(
        message,
        border_style="green" if not dry_run else "yellow",
        padding=(1, 2),
    )
    console.print()
    console.print(panel)
