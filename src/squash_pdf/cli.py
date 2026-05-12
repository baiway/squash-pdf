"""squash-pdf: compress vector-heavy PDFs by rasterising their pages."""

from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path

import click
import img2pdf


def _find_ghostscript() -> str:
    gs = shutil.which("gs")
    if gs is None:
        raise click.ClickException(
            "Ghostscript not found.\n"
            "  macOS:  brew install ghostscript\n"
            "  Linux:  apt install ghostscript"
        )
    return gs


def _rasterise(input_pdf: Path, out_dir: Path, dpi: int, gs: str) -> list[Path]:
    try:
        subprocess.run(
            [
                gs,
                "-sDEVICE=png16m",
                f"-r{dpi}",
                "-dNOPAUSE",
                "-dBATCH",
                "-dQUIET",
                f"-sOutputFile={out_dir / 'page_%03d.png'}",
                str(input_pdf),
            ],
            check=True,
            capture_output=True,
        )
    except subprocess.CalledProcessError as e:
        raise click.ClickException(
            f"Ghostscript failed:\n{e.stderr.decode(errors='replace')}"
        ) from e

    return sorted(out_dir.glob("page_*.png"))


@click.command()
@click.argument("input_pdf", type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.argument("output_pdf", type=click.Path(dir_okay=False, path_type=Path), required=False)
@click.option("--dpi", default=300, show_default=True, metavar="DPI", help="Rasterisation resolution.")
@click.option("--force", "-f", is_flag=True, help="Overwrite output file if it exists.")
def main(input_pdf: Path, output_pdf: Path | None, dpi: int, force: bool) -> None:
    """Compress a PDF by rasterising its pages.

    Particularly effective for vector-heavy PDFs such as GoodNotes exports,
    where standard compression tools have little effect because the content
    is stored as paths rather than images.

    OUTPUT_PDF defaults to <input>-compressed.pdf in the same directory.
    """
    gs = _find_ghostscript()

    if output_pdf is None:
        output_pdf = input_pdf.with_stem(input_pdf.stem + "-compressed")

    if output_pdf.exists() and not force:
        raise click.ClickException(
            f"'{output_pdf}' already exists. Pass --force to overwrite."
        )

    input_mb = input_pdf.stat().st_size / 1_000_000

    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)

        click.echo(f"Rasterising {input_pdf.name} at {dpi} DPI...")
        pages = _rasterise(input_pdf, tmp_dir, dpi, gs)

        page_word = "page" if len(pages) == 1 else "pages"
        click.echo(f"Stitching {len(pages)} {page_word}...")
        output_pdf.write_bytes(img2pdf.convert([str(p) for p in pages]))

    output_mb = output_pdf.stat().st_size / 1_000_000
    reduction = (1 - output_mb / input_mb) * 100
    click.echo(f"Done: {input_mb:.1f} MB -> {output_mb:.1f} MB ({reduction:.0f}% smaller)")
