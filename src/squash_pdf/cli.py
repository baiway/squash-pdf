"""squash-pdf: compress vector-heavy PDFs by rasterising their pages."""

from __future__ import annotations

import argparse
from pathlib import Path

import fitz


def _rasterise(input_pdf: Path, output_pdf: Path, dpi: int) -> int:
    src = fitz.open(str(input_pdf))
    out = fitz.open()
    for page in src:
        pix = page.get_pixmap(dpi=dpi)
        img_page = out.new_page(width=page.rect.width, height=page.rect.height)
        img_page.insert_image(img_page.rect, stream=pix.tobytes("jpeg"))
    out.save(str(output_pdf))
    return len(src)


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Compress a PDF by rasterising its pages. Particularly effective for "
            "vector-heavy PDFs such as GoodNotes exports, where standard compression "
            "tools have little effect because the content is stored as paths rather "
            "than images."
        )
    )
    parser.add_argument("input_pdf", type=Path, help="Input PDF file.")
    parser.add_argument(
        "output_pdf",
        type=Path,
        nargs="?",
        help="Output PDF file (default: <input>-compressed.pdf).",
    )
    parser.add_argument(
        "--dpi",
        type=int,
        default=300,
        metavar="DPI",
        help="Rasterisation resolution (default: %(default)s).",
    )
    parser.add_argument(
        "-f", "--force",
        action="store_true",
        help="Overwrite output file if it exists.",
    )

    args = parser.parse_args()
    input_pdf: Path = args.input_pdf
    output_pdf: Path | None = args.output_pdf

    if not input_pdf.exists() or input_pdf.is_dir():
        parser.error(f"'{input_pdf}' is not a valid file.")

    if output_pdf is None:
        output_pdf = input_pdf.with_stem(input_pdf.stem + "-compressed")

    if output_pdf.exists() and not args.force:
        parser.error(f"'{output_pdf}' already exists. Pass --force to overwrite.")

    input_mb = input_pdf.stat().st_size / 1_000_000

    print(f"Rasterising {input_pdf.name} at {args.dpi} DPI...")
    n_pages = _rasterise(input_pdf, output_pdf, args.dpi)

    output_mb = output_pdf.stat().st_size / 1_000_000
    reduction = (1 - output_mb / input_mb) * 100
    page_word = "page" if n_pages == 1 else "pages"
    print(f"Done: {n_pages} {page_word}, {input_mb:.1f} MB -> {output_mb:.1f} MB ({reduction:.0f}% smaller)")
