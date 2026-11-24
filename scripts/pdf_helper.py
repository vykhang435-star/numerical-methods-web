"""Inspect a PDF's bookmarks, extract text, or render a full page."""

import argparse
from pathlib import Path

import fitz


RENDER_DPI = 200


def print_toc(doc):
    entries = doc.get_toc()
    print(f"{doc.page_count} page(s)")
    if not entries:
        print("No embedded table of contents (PDF bookmarks) found.")
        return

    print(f"Embedded table of contents: {len(entries)} entries")
    for level, title, page in entries:
        destination = f"p. {page}" if page > 0 else "no local page"
        print(f"{'  ' * (level - 1)}- {title} [{destination}]")


def validate_page_range(doc, start_page, end_page):
    if not 1 <= start_page <= end_page <= doc.page_count:
        raise ValueError(
            f"Invalid page range {start_page}-{end_page}; expected "
            f"1 <= start_page <= end_page <= {doc.page_count}."
        )


def extract_text(doc, start_page, end_page, out_txt):
    with out_txt.open("w", encoding="utf-8") as output:
        for page_index in range(start_page - 1, end_page):
            text = doc[page_index].get_text("text")
            output.write(text)
            if not text.endswith("\n"):
                output.write("\n")


def render_page(doc, page_num, out_png):
    zoom = RENDER_DPI / 72
    pixmap = doc[page_num - 1].get_pixmap(matrix=fitz.Matrix(zoom, zoom))
    pixmap.set_dpi(RENDER_DPI, RENDER_DPI)
    pixmap.save(str(out_png), output="png")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)

    toc = commands.add_parser("toc", help="List embedded PDF bookmarks.")
    toc.add_argument("pdf_path", type=Path)

    extract = commands.add_parser("extract", help="Extract an inclusive range of pages.")
    extract.add_argument("pdf_path", type=Path)
    extract.add_argument("start_page", type=int, help="First page (1-based).")
    extract.add_argument("end_page", type=int, help="Last page (inclusive).")
    extract.add_argument("out_txt", type=Path)

    crop = commands.add_parser("crop", help="Render a full page as a 200 DPI PNG.")
    crop.add_argument("pdf_path", type=Path)
    crop.add_argument("page_num", type=int, help="Page to render (1-based).")
    crop.add_argument("out_png", type=Path)

    args = parser.parse_args()
    try:
        with fitz.open(str(args.pdf_path)) as doc:
            if not doc.is_pdf:
                raise ValueError(f"Not a PDF: {args.pdf_path}")
            if doc.needs_pass:
                raise ValueError(f"PDF requires a password: {args.pdf_path}")

            if args.command == "toc":
                print_toc(doc)
                return

            if args.command == "extract":
                first, last, output = args.start_page, args.end_page, args.out_txt
            else:
                first = last = args.page_num
                output = args.out_png

            validate_page_range(doc, first, last)
            if output.exists() and output.samefile(args.pdf_path):
                raise ValueError("The output path must not overwrite the input PDF.")

            if args.command == "extract":
                extract_text(doc, first, last, output)
            else:
                render_page(doc, first, output)
    except (OSError, RuntimeError, ValueError) as exc:
        parser.exit(1, f"{parser.prog}: error: {exc}\n")


if __name__ == "__main__":
    main()
