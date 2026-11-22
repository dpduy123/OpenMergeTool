#!/usr/bin/env python3
"""
Convert_JPG_to_PDF.py - Convert one or more JPG images into a single PDF.

Each image becomes one page, in the order given.

Usage:
    python Convert_JPG_to_PDF.py <image1.jpg> [image2.jpg ...]
                                 [--page-size image|a4|letter] [--margin 36]
                                 [--dpi 150] [--job-id ID] [--output-dir output]

If no paths are given on the command line, the script prompts for one.
The result is saved to: <output-dir>/<job_id>/converted.pdf
"""

import argparse
import re
import sys
import uuid
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageOps

VALID_EXT = {".jpg", ".jpeg"}
JPEG_MAGIC = b"\xff\xd8\xff"
JOB_ID_RE = re.compile(r"^[A-Za-z0-9_-]{1,64}$")

# Page sizes in points (1 pt = 1/72 inch), portrait orientation.
PAGE_SIZES = {
    "a4": (595, 842),
    "letter": (612, 792),
}


def clean_path(path_str: str) -> Path:
    path_str = (path_str or "").strip().strip('"').strip("'")
    if not path_str:
        raise ValueError("Empty file path")
    return Path(path_str).expanduser()


def validate_jpg(path_str: str) -> Path:
    path = clean_path(path_str)
    if not path.is_file():
        raise FileNotFoundError(f"File not found: {path}")
    if path.suffix.lower() not in VALID_EXT:
        raise ValueError(f"Not a JPG file (extension): {path}")
    with open(path, "rb") as f:
        if f.read(3) != JPEG_MAGIC:
            raise ValueError(f"Not a JPG file (content): {path}")
    return path


def validate_job_id(job_id: str) -> str:
    if not JOB_ID_RE.match(job_id):
        raise ValueError("Job ID may only contain letters, digits, '_' and '-' (max 64 chars)")
    return job_id


def load_image(path: Path) -> Image.Image:
    try:
        img = Image.open(path)
        img = ImageOps.exif_transpose(img)  # respect camera rotation
        return img.convert("RGB")
    except Exception as e:
        raise ValueError(f"Cannot read image {path}: {e}") from e


def place_on_page(img: Image.Image, page_size: str, margin_pt: float, dpi: int) -> Image.Image:
    """Fit the image inside a fixed page (A4/Letter), centred, on a white background."""
    w_pt, h_pt = PAGE_SIZES[page_size]
    if img.width > img.height:  # landscape image -> landscape page
        w_pt, h_pt = h_pt, w_pt

    scale = dpi / 72
    page_w, page_h = round(w_pt * scale), round(h_pt * scale)
    margin = round(margin_pt * scale)
    box_w, box_h = page_w - 2 * margin, page_h - 2 * margin
    if box_w <= 0 or box_h <= 0:
        raise ValueError("Margin is too large for the page size")

    ratio = min(box_w / img.width, box_h / img.height)
    new_size = (max(1, round(img.width * ratio)), max(1, round(img.height * ratio)))
    img = img.resize(new_size, Image.LANCZOS)

    page = Image.new("RGB", (page_w, page_h), (255, 255, 255))
    page.paste(img, ((page_w - img.width) // 2, (page_h - img.height) // 2))
    return page


def new_job_id() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S") + "_" + uuid.uuid4().hex[:8]


def run(files, page_size: str = "image", margin: float = 36, dpi: int = 150,
        job_id: str = None, output_dir: str = "output") -> Path:
    if not files:
        raise ValueError("Need at least 1 JPG file")
    if page_size != "image" and page_size not in PAGE_SIZES:
        raise ValueError(f"Unknown page size: {page_size}")
    if not 36 <= dpi <= 1200:
        raise ValueError("DPI must be between 36 and 1200")
    if margin < 0:
        raise ValueError("Margin cannot be negative")

    paths = [validate_jpg(f) for f in files]
    job_id = validate_job_id(job_id) if job_id else new_job_id()

    pages = []
    for path in paths:
        img = load_image(path)
        if page_size != "image":
            img = place_on_page(img, page_size, margin, dpi)
        pages.append(img)

    out_dir = Path(output_dir) / job_id
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "converted.pdf"
    pages[0].save(out_path, "PDF", save_all=True, append_images=pages[1:],
                  resolution=dpi)
    return out_path


def main():
    parser = argparse.ArgumentParser(description="Convert JPG images into a single PDF.")
    parser.add_argument("files", nargs="*", help="JPG files, one page each, in order")
    parser.add_argument("-s", "--page-size", choices=["image", *PAGE_SIZES], default="image",
                        help="'image' = page matches each image; a4/letter = fit image on that page")
    parser.add_argument("-m", "--margin", type=float, default=36,
                        help="Margin in points for a4/letter (72 pt = 1 inch, default 36)")
    parser.add_argument("--dpi", type=int, default=150,
                        help="Resolution; sets physical page size for 'image' mode (default 150)")
    parser.add_argument("-j", "--job-id", help="Job ID (default: auto-generated)")
    parser.add_argument("-o", "--output-dir", default="output", help="Base output folder")
    args = parser.parse_args()

    files = args.files or [input("Path to JPG: ")]

    try:
        out_path = run(files, args.page_size, args.margin, args.dpi, args.job_id, args.output_dir)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"PDF saved to: {out_path} ({len(files)} page{'s' if len(files) != 1 else ''})")


if __name__ == "__main__":
    main()
