"""Export the 19 requested Logan 5e Chapter 4 beam figures at 300 DPI."""

import argparse
from pathlib import Path

import pymupdf as fitz

DEFAULT_PDF = Path("D:/pps/a-first-course-in-the-fem-5e-logan.pdf")
DEFAULT_OUTPUT_DIR = Path(__file__).resolve().parents[1] / "public" / "images"
DPI = 300

# Verified against the local edition. PDF point coordinates from top left;
# some supplied windows needed extension to keep diagrams or captions intact.
FIGURES = {
    9: (223, (40, 386, 485, 499)),
    10: (223, (40, 500, 485, 610)),
    11: (224, (40, 50, 485, 151)),
    12: (224, (40, 222, 485, 314)),
    13: (224, (40, 406, 265, 488)),
    14: (224, (265, 406, 485, 488)),
    15: (225, (40, 49, 295, 158)),
    16: (225, (307, 49, 490, 158)),
    18: (225, (114, 381, 365, 460)),
    19: (225, (40, 508, 485, 615)),
    20: (226, (40, 50, 485, 189)),
    21: (226, (40, 193, 485, 290)),
    22: (226, (40, 294, 485, 400)),
    23: (226, (40, 403, 485, 521)),
    26: (227, (307, 103, 490, 205)),
    27: (227, (113, 222, 298, 332)),
    37: (229, (110, 273, 291, 361)),
    38: (229, (311, 273, 490, 361)),
    39: (229, (110, 479, 298, 570)),
}


def figure_name(number):
    return f"logan_fig_p4_{number}_beam.png"


def crop_figures(pdf_path, output_dir):
    with fitz.open(pdf_path) as doc:
        if len(doc) <= max(index for index, _ in FIGURES.values()):
            raise ValueError("The PDF does not contain all required pages.")
        jobs = []
        for number, (index, bounds) in FIGURES.items():
            page, rect = doc[index], fitz.Rect(bounds)
            if not page.rect.contains(rect):
                raise ValueError(f"Figure P4–{number}: crop outside PDF page {index + 1}.")
            jobs.append((number, index, rect))

        output_dir.mkdir(parents=True, exist_ok=True)
        for number, index, rect in jobs:
            pix = doc[index].get_pixmap(clip=rect, dpi=DPI, alpha=False, annots=False)
            path = output_dir / figure_name(number)
            pix.save(path)
            print(f"{path.name}: {pix.width} x {pix.height} px, {DPI} DPI (PDF page {index + 1})")
    print(f"Exported {len(jobs)} PNGs to {output_dir}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pdf", type=Path, default=DEFAULT_PDF)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()
    try:
        crop_figures(args.pdf, args.output_dir)
    except (OSError, RuntimeError, ValueError) as exc:
        parser.exit(1, f"Error: {exc}\n")


if __name__ == "__main__":
    main()
