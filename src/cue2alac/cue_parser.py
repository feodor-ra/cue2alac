"""CUE sheet parsing utilities."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from .models import CueInfo, CueTrack

if TYPE_CHECKING:
    from pathlib import Path

_TIME_MM_SS_FF = re.compile(r"^\s*(\d+):(\d+):(\d+)\s*$")


def cue_time_to_seconds(time_str: str) -> float:
    """
    Convert CUE INDEX time to seconds.

    CUE INDEX time is usually MM:SS:FF where FF is 1/75 sec.

    Args:
        time_str (str): Time string in MM:SS:FF format.

    Returns:
        float: Time in seconds.

    Raises:
        ValueError: If time format is invalid.

    """
    m = _TIME_MM_SS_FF.match(time_str)
    if not m:
        msg = f"Unrecognized CUE time format: {time_str!r} (expected MM:SS:FF)"
        raise ValueError(msg)
    mm, ss, ff = map(int, m.groups())
    return mm * 60 + ss + ff / 75.0


def parse_cue(cue_path: Path) -> CueInfo:  # noqa: C901, PLR0912, PLR0915
    """
    Parse CUE sheet file.

    Parses common CUE sheet fields:
    - Global: TITLE, PERFORMER, REM DATE, REM GENRE
    - Track: TRACK nn AUDIO, TITLE, PERFORMER, INDEX 01 mm:ss:ff

    Args:
        cue_path (Path): Path to CUE sheet file.

    Returns:
        CueInfo: Parsed CUE information.

    Raises:
        ValueError: If no valid tracks found in CUE.

    """
    # Try a couple of common encodings (CUEs can be messy).
    raw: str | None = None
    for enc in ("utf-8", "cp1251", "latin-1"):
        try:
            raw = cue_path.read_text(encoding=enc)
            break
        except UnicodeDecodeError:
            continue
    if raw is None:
        raw = cue_path.read_text(encoding="utf-8", errors="replace")

    info = CueInfo()
    current: CueTrack | None = None

    for line in map(str.strip, raw.splitlines()):
        if not line:
            continue

        # REM DATE / REM GENRE
        if line.upper().startswith("REM "):
            # e.g. REM DATE 1999
            parts = line.split(None, 2)
            if len(parts) >= 3:  # noqa: PLR2004
                key = parts[1].upper()
                val = _unquote(parts[2])
                if key == "DATE" and not info.date:
                    info.date = val
                elif key == "GENRE" and not info.genre:
                    info.genre = val
            continue

        # TRACK start
        if line.upper().startswith("TRACK "):
            # TRACK 01 AUDIO
            parts = line.split()
            if len(parts) >= 2 and parts[1].isdigit():  # noqa: PLR2004
                current = CueTrack(number=int(parts[1]))
                info.tracks.append(current)
            continue

        # TITLE / PERFORMER can be global (before TRACK) or per-track
        if line.upper().startswith("TITLE "):
            val = _unquote(line[6:])
            if current is None:
                if not info.album:
                    info.album = val
            else:
                current.title = val
            continue

        if line.upper().startswith("PERFORMER "):
            val = _unquote(line[10:])
            if current is None:
                if not info.album_artist:
                    info.album_artist = val
            else:
                current.performer = val
            continue

        # INDEX 01
        if line.upper().startswith("INDEX "):
            # INDEX 01 00:00:00
            parts = line.split()
            if len(parts) >= 3 and current is not None:  # noqa: PLR2004
                idx = parts[1]
                t = parts[2]
                if idx == "01":
                    current.index01_seconds = cue_time_to_seconds(t)
            continue

    # Basic validation
    info.tracks = [t for t in info.tracks if t.index01_seconds is not None]
    if not info.tracks:
        msg = "No tracks with INDEX 01 found in CUE. Check the CUE format."
        raise ValueError(msg)

    # Sort by track number just in case
    info.tracks.sort(key=lambda t: t.number)
    return info


def _unquote(s: str) -> str:
    s = s.strip()
    if len(s) >= 2 and s[0] == '"' and s[-1] == '"':  # noqa: PLR2004
        return s[1:-1]
    return s
