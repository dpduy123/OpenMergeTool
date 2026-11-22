#!/usr/bin/env python3
"""
Merge_JPG.py - Merge two JPG images into one JPG.

Usage:
    python Merge_JPG.py <image1.jpg> <image2.jpg> [--direction horizontal|vertical]
                        [--job-id ID] [--output-dir output] [--quality 95]

If paths are not given on the command line, the script prompts for them.
The result is saved to: <output-dir>/<job_id>/merged.jpg
"""

import argparse
import sys
import uuid
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageOps

VALID_EXT = {".jpg", ".jpeg"}


def load_image(path_str: str) -> Image.Image:
    path = Path(path_str.strip().strip('"').strip("'")).expanduser()
    if not path.is_file():
        raise FileNotFoundError(f"File not found: {path}")
    if path.suffix.lower() not in VALID_EXT:
        raise ValueError(f"Not a JPG file: {path}")
    img = Image.open(path)
    img = ImageOps.exif_transpose(img)  # respect camera rotation
    return img.convert("RGB")


def merge_images(img1: Image.Image, img2: Image.Image, direction: str = "horizontal",
                 background=(255, 255, 255)) -> Image.Image:
    if direction == "horizontal":
        # Scale both images to the same height (the smaller one) to avoid upscaling.
        h = min(img1.height, img2.height)
        img1 = img1.resize((round(img1.width * h / img1.height), h), Image.LANCZOS)
        img2 = img2.resize((round(img2.width * h / img2.height), h), Image.LANCZOS)
        merged = Image.new("RGB", (img1.width + img2.width, h), background)
        merged.paste(img1, (0, 0))
        merged.paste(img2, (img1.width, 0))
    elif direction == "vertical":
        # Scale both images to the same width (the smaller one).
        w = min(img1.width, img2.width)
        img1 = img1.resize((w, round(img1.height * w / img1.width)), Image.LANCZOS)
        img2 = img2.resize((w, round(img2.height * w / img2.width)), Image.LANCZOS)
        merged = Image.new("RGB", (w, img1.height + img2.height), background)
        merged.paste(img1, (0, 0))
        merged.paste(img2, (0, img1.height))
    else:
        raise ValueError("direction must be 'horizontal' or 'vertical'")
    return merged


def new_job_id() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S") + "_" + uuid.uuid4().hex[:8]


def run(file1: str, file2: str, direction: str = "horizontal", job_id: str = None,
        output_dir: str = "output", quality: int = 95) -> Path:
    img1 = load_image(file1)
    img2 = load_image(file2)
    merged = merge_images(img1, img2, direction)

    job_id = job_id or new_job_id()
    out_dir = Path(output_dir) / job_id
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "merged.jpg"
    merged.save(out_path, "JPEG", quality=quality)
    return out_path


def main():
    parser = argparse.ArgumentParser(description="Merge 2 JPG files into one JPG.")
    parser.add_argument("file1", nargs="?", help="Path to first JPG")
    parser.add_argument("file2", nargs="?", help="Path to second JPG")
    parser.add_argument("-d", "--direction", choices=["horizontal", "vertical"],
                        default="horizontal", help="Merge side by side or top/bottom")
    parser.add_argument("-j", "--job-id", help="Job ID (default: auto-generated)")
    parser.add_argument("-o", "--output-dir", default="output", help="Base output folder")
    parser.add_argument("-q", "--quality", type=int, default=95, help="JPEG quality 1-95")
    args = parser.parse_args()

    file1 = args.file1 or input("Path to first JPG: ")
    file2 = args.file2 or input("Path to second JPG: ")

    try:
        out_path = run(file1, file2, args.direction, args.job_id, args.output_dir, args.quality)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"Merged image saved to: {out_path}")


if __name__ == "__main__":
    main()
