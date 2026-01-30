# cue2alac

Convert single FLAC audio image + CUE sheet into individual ALAC tracks with full metadata and cover art.

Perfect for Apple Music and iTunes - creates properly tagged .m4a files from your CD rips.

## Features

- **CUE sheet parsing** - Supports common CUE formats with UTF-8, CP1251, and Latin-1 encodings
- **ALAC encoding** - High-quality lossless audio format compatible with Apple devices
- **Full metadata** - Album, artist, track number, date, genre, and cover art
- **Track splitting** - Accurately splits audio by CUE INDEX markers
- **Flexible metadata** - Override album/artist/date/genre from command line
- **Dry run mode** - Preview ffmpeg commands before execution

## Usage

### Basic usage

```bash
uvx --from git+https://github.com/feodor-ra/cue2alac.git@0.1.0 cue2alac --audio album.flac --cue album.cue --cover cover.jpg
```

### Options

```plain
--audio PATH            Input FLAC image file (required)
--cue PATH              CUE sheet file (required)
--cover PATH            Cover image file (jpg/png, optional)
--outdir PATH           Output directory (default: ALAC)
--album TEXT            Override album title
--album-artist TEXT     Override album artist
--date TEXT             Override date/year
--genre TEXT            Override genre
--dry-run               Print ffmpeg commands without running them
--help                  Show help message
```

### Examples

Split with all metadata from CUE:

```bash
uvx --from git+https://github.com/feodor-ra/cue2alac.git@0.1.0 cue2alac --audio album.flac --cue album.cue --cover cover.jpg
```

Override album artist:

```bash
uvx --from git+https://github.com/feodor-ra/cue2alac.git@0.1.0 cue2alac --audio album.flac --cue album.cue --album-artist "Different Artist" --outdir ./output
```

Dry run to preview commands:

```bash
uvx --from git+https://github.com/feodor-ra/cue2alac.git@0.1.0 cue2alac --audio album.flac --cue album.cue --dry-run
```
