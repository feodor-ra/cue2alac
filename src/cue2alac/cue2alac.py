"""CLI entry point for CUE to ALAC splitter."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from .splitter import CueSplitter

app = typer.Typer()


@app.command()
def main(  # noqa: PLR0913, PLR0917
    audio: Annotated[Path, typer.Option(help="Input FLAC image file")],
    cue: Annotated[Path, typer.Option(help="CUE sheet file")],
    cover: Annotated[
        Path | None,
        typer.Option(help="Cover image (jpg/png). Optional"),
    ] = None,
    outdir: Annotated[
        Path,
        typer.Option(help="Output directory (default: ALAC)"),
    ] = Path("ALAC"),
    album: Annotated[
        str,
        typer.Option(help="Override album title (default: from CUE)"),
    ] = "",
    album_artist: Annotated[
        str,
        typer.Option(
            help="Override album artist (default: from CUE)",
        ),
    ] = "",
    date: Annotated[
        str,
        typer.Option(help="Override date/year (default: from CUE REM DATE)"),
    ] = "",
    genre: Annotated[
        str,
        typer.Option(help="Override genre (default: from CUE REM GENRE)"),
    ] = "",
    dry_run: Annotated[  # noqa: FBT002
        bool,
        typer.Option(
            help="Print ffmpeg commands without running them",
        ),
    ] = False,
) -> None:
    """
    Split single FLAC + CUE into ALAC .m4a tracks with cover and metadata.

    Apple Music-friendly output with full metadata support.
    """
    splitter = CueSplitter(
        audio=audio,
        cue=cue,
        cover=cover,
        album_override=album,
        album_artist_override=album_artist,
        date_override=date,
        genre_override=genre,
    )
    splitter.split(outdir, dry_run=dry_run)


if __name__ == "__main__":
    app()
