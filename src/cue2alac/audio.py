"""Audio file operations and metadata handling."""

from __future__ import annotations

import re
import subprocess
from typing import TYPE_CHECKING

import rich

if TYPE_CHECKING:
    from pathlib import Path


def ffprobe_duration_seconds(audio_path: Path) -> float:
    """
    Get audio duration using ffprobe.

    Args:
        audio_path (Path): Path to audio file.

    Returns:
        float: Duration in seconds.

    Raises:
        RuntimeError: If ffprobe fails.

    """
    cmd = [
        "ffprobe",
        "-v",
        "error",
        "-show_entries",
        "format=duration",
        "-of",
        "default=nk=1:nw=1",
        str(audio_path),
    ]
    p = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        check=True,
    )
    if p.returncode != 0:
        msg = f"ffprobe failed:\n{p.stderr}"
        raise RuntimeError(msg)
    return float(p.stdout.strip())


def safe_filename(s: str) -> str:
    """
    Sanitize string to use as filename.

    Args:
        s (str): Original string.

    Returns:
        str: Sanitized filename.

    """
    s = s.strip()
    s = re.sub(r'[\/:*?"<>|]', "_", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s or "Track"


def run_ffmpeg_extract_to_alac(  # noqa: PLR0913
    *,
    audio: Path,
    cover: Path | None,
    out_file: Path,
    start: float,
    duration: float,
    album: str,
    album_artist: str,
    artist: str,
    title: str,
    track_num: int,
    track_total: int,
    date: str,
    genre: str,
    dry_run: bool,
) -> None:
    """
    Extract audio segment and encode to ALAC with metadata.

    Args:
        audio (Path): Input audio file.
        cover (Path | None): Cover image file (optional).
        out_file (Path): Output ALAC file.
        start (float): Start time in seconds.
        duration (float): Duration in seconds.
        album (str): Album title for metadata.
        album_artist (str): Album artist for metadata.
        artist (str): Track artist for metadata.
        title (str): Track title for metadata.
        track_num (int): Track number.
        track_total (int): Total number of tracks.
        date (str): Release date for metadata.
        genre (str): Genre for metadata.
        dry_run (bool): If True, print command without executing.

    Raises:
        RuntimeError: If ffmpeg fails.

    """
    cmd = ["ffmpeg", "-hide_banner", "-y"]

    cmd += ["-i", str(audio)]
    if cover is not None:
        cmd += ["-i", str(cover)]

    cmd += ["-map", "0:a:0"]
    if cover is not None:
        cmd += ["-map", "1:v:0"]
    cmd += [
        "-c:a",
        "alac",
        "-metadata",
        f"album={album}",
        "-metadata",
        f"album_artist={album_artist}",
        "-metadata",
        f"albumartist={album_artist}",
        "-metadata",
        f"artist={artist}",
        "-metadata",
        f"title={title}",
        "-metadata",
        f"track={track_num}/{track_total}",
    ]

    if date:
        cmd += ["-metadata", f"date={date}", "-metadata", f"year={date}"]
    if genre:
        cmd += ["-metadata", f"genre={genre}"]

    if cover is not None:
        cmd += [
            "-c:v",
            "mjpeg",
            "-disposition:v:0",
            "attached_pic",
            "-metadata:s:v:0",
            "title=Cover (front)",
            "-metadata:s:v:0",
            "comment=Cover (front)",
        ]

    cmd += [
        "-ss",
        f"{start:.6f}",
        "-t",
        f"{duration:.6f}",
        "-movflags",
        "+faststart",
        str(out_file),
    ]

    if dry_run:
        rich.print("DRY RUN:", " ".join(cmd))
        return

    p = subprocess.run(
        cmd,
        text=True,
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.STDOUT,
    )
    if p.returncode != 0:
        msg = f"ffmpeg failed for {out_file.name}"
        raise RuntimeError(msg)
