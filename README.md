# squash-pdf

Compresses vector-heavy PDFs by rasterising their pages. Particularly effective for [GoodNotes](https://www.goodnotes.com/) exports, which store handwriting as dense vector paths that standard PDF compressors can't touch. A typical GoodNotes export might go from 24 MB to 2.4 MB at 300 DPI — sharp enough to read comfortably on screen or print.

## Prerequisites

Ghostscript must be installed:

```sh
# macOS
brew install ghostscript

# Debian / Ubuntu
apt install ghostscript
```

## Installation

```sh
git clone https://github.com/baiway/squash-pdf
cd squash-pdf
uv sync
```

Run without activating the virtualenv:

```sh
uv run squash-pdf notes.pdf
```

Or activate first:

```sh
source .venv/bin/activate
squash-pdf notes.pdf
```

## Usage

```
squash-pdf [OPTIONS] INPUT_PDF [OUTPUT_PDF]
```

| Argument / Option | Default | Description |
|---|---|---|
| `INPUT_PDF` | — | PDF to compress |
| `OUTPUT_PDF` | `<input>-compressed.pdf` | Output path |
| `--dpi DPI` | `300` | Rasterisation resolution |
| `--force` / `-f` | off | Overwrite output if it exists |

### Examples

```sh
# Compress with defaults (300 DPI, output alongside input)
squash-pdf lecture-notes.pdf

# Specify an output path
squash-pdf lecture-notes.pdf lecture-notes-small.pdf

# Lower DPI for smaller files (fine for screenshots, rougher for handwriting)
squash-pdf lecture-notes.pdf --dpi 200

# Overwrite an existing output
squash-pdf lecture-notes.pdf --force
```
