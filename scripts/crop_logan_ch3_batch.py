"""Crop the Chapter 3 figures from the supplied Logan 5e PDF at 300 DPI."""

import argparse
from pathlib import Path

import pymupdf as fitz

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PDF = Path("D:/pps/a-first-course-in-the-fem-5e-logan.pdf")
DPI = 300

# One-based PDF page numbers and rectangles in PDF points, measured from
# the supplied edition. Include captions, arrowheads and dimension lines.
# In particular, P3-22/P3-27/P3-49 extend outside the initial crop estimates.
FIGURES = {
    "2_bar": (152, (120, 57, 389, 118)),
    "3_bar": (152, (120, 124, 415, 192)),
    "4_bar": (152, (120, 198, 434, 265)),
    "5_bar": (152, (120, 271, 415, 331)),
    "7_bar": (152, (120, 468, 413, 540)),
    "8_bar": (152, (120, 547, 391, 612)),
    "9_bar": (153, (95, 56, 377, 118)),
    "10_bar": (153, (96, 123, 382, 196)),
    "20_truss": (157, (94, 104, 273, 259)),
    "22_truss": (157, (94, 385, 341, 612)),
    "27_truss": (158, (122, 434, 381, 612)),
    "33a_truss": (160, (120, 63, 330, 224)),
    "33b_truss": (160, (368, 57, 489, 224)),
    "49_truss": (165, (94, 296, 302, 394)),
    "50_truss": (165, (94, 413, 199, 534)),
    "51_truss": (165, (294, 437, 463, 534)),
}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pdf", type=Path, default=DEFAULT_PDF)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "public" / "images")
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    with fitz.open(args.pdf) as pdf:
        for figure, (page_number, bounds) in FIGURES.items():
            page = pdf[page_number - 1]
            clip = fitz.Rect(bounds)
            if not page.rect.contains(clip):
                raise ValueError(f"P3-{figure}: crop is outside PDF page {page_number}")
            path = args.output_dir / f"logan_fig_p3_{figure}.png"
            image = page.get_pixmap(dpi=DPI, clip=clip, alpha=False)
            image.save(path)
            print(f"{path.name}: PDF p. {page_number}, {image.width}x{image.height} @ {DPI} DPI")
    print(f"Exported {len(FIGURES)} figures.")


if __name__ == "__main__":
    main()
