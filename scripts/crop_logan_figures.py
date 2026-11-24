"""Crop six Logan 5e figures from the local PDF at 300 DPI."""

import argparse
from pathlib import Path

import pymupdf as fitz


DEFAULT_PDF = Path("D:/pps/a-first-course-in-the-fem-5e-logan.pdf")
DEFAULT_OUTPUT_DIR = Path(__file__).resolve().parents[1] / "public" / "images"
DPI = 300

# Zero-based PDF page indices; rectangles use PDF points from the top left.
FIGURES = (
    ("logan_fig_p3_23_truss.png", 157, fitz.Rect(75, 105, 255, 275)),
    # Extend the requested box left and up to keep node 1 and the top load arrow.
    ("logan_fig_p3_24_truss.png", 157, fitz.Rect(263, 100, 485, 275)),
    # Both figures are on PDF page 159 (printed page 140), not PDF page 160.
    ("logan_fig_p3_29_truss.png", 158, fitz.Rect(94, 145, 303, 329)),
    ("logan_fig_p3_30_truss.png", 158, fitz.Rect(354, 145, 465, 329)),
    ("logan_fig_p4_6_beam.png", 223, fitz.Rect(40, 50, 480, 170)),
    ("logan_fig_p4_8_fixed_beam.png", 223, fitz.Rect(40, 285, 480, 385)),
)


def crop_figures(pdf_path: Path, output_dir: Path) -> None:
    with fitz.open(pdf_path) as doc:
        if len(doc) <= max(index for _, index, _ in FIGURES):
            raise ValueError("The PDF does not contain all required pages.")
        for filename, index, rect in FIGURES:
            if not doc[index].rect.contains(rect):
                raise ValueError(f"The crop for {filename} is outside PDF page {index + 1}.")

        output_dir.mkdir(parents=True, exist_ok=True)
        for filename, index, rect in FIGURES:
            image = doc[index].get_pixmap(clip=rect, dpi=DPI, alpha=False, annots=False)
            output_path = output_dir / filename
            image.save(output_path)
            print(f"{output_path} ({image.width} x {image.height} px, {DPI} DPI, PDF page {index + 1})")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pdf", type=Path, default=DEFAULT_PDF, help="Path to the Logan PDF")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR, help="PNG output directory")
    args = parser.parse_args()
    try:
        crop_figures(args.pdf, args.output_dir)
    except (OSError, RuntimeError, ValueError) as exc:
        parser.exit(1, f"Error: {exc}\n")


if __name__ == "__main__":
    main()
