"""Data models for CUE sheet and track information."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class CueTrack:
    """Represents a single track from a CUE sheet."""

    number: int
    title: str = ""
    performer: str = ""
    index01_seconds: float | None = None


@dataclass
class CueInfo:
    """Parsed CUE sheet information."""

    album: str = ""
    album_artist: str = ""
    date: str = ""
    genre: str = ""
    tracks: list[CueTrack] = field(default_factory=list)
