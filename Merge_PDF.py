#!/usr/bin/env python3
"""
Merge_PDF.py - Merge two (or more) PDF files into one PDF.

Usage:
    python Merge_PDF.py <file1.pdf> <file2.pdf> [more.pdf ...]
                        [--job-id ID] [--output-dir output] [--password PWD]

If no paths are given on the command line, the script prompts for two.
Pages are appended in the order the files are given.
The result is saved to: <output-dir>/<job_id>/merged.pdf
"""

import argparse
import re
import sys
import uuid
from datetime import datetime
from pathlib import Path

from pypdf import PdfReader, PdfWriter
from pypdf.errors import PdfReadError

JOB_ID_RE = re.compile(r"^[A-Za-z0-9_-]{1,64}$")


def clean_path(path_str: str) -> Path:
    path_str = (path_str or "").strip().strip('"').strip("'")
    if not path_str:
        raise ValueError("Empty file path")
    return Path(path_str).expanduser()


def validate_pdf(path_str: str) -> Path:
    path = clean_path(path_str)
    if not path.is_file():
        raise FileNotFoundError(f"File not found: {path}")
    if path.suffix.lower() != ".pdf":
        raise ValueError(f"Not a PDF file (extension): {path}")
    with open(path, "rb") as f:
        # PDF header may be preceded by a few junk bytes; spec allows it within the first 1024.
        if b"%PDF-" not in f.read(1024):
            raise ValueError(f"Not a PDF file (content): {path}")
    return path


def validate_job_id(job_id: str) -> str:
    if not JOB_ID_RE.match(job_id):
        raise ValueError("Job ID may only contain letters, digits, '_' and '-' (max 64 chars)")
    return job_id


def open_reader(path: Path, password: str = None) -> PdfReader:
    try:
        reader = PdfReader(path)
    except PdfReadError as e:
        raise ValueError(f"Cannot read PDF {path}: {e}") from e
    if reader.is_encrypted:
        # Many PDFs are encrypted with an empty user password; try that first.
        if not reader.decrypt(password or ""):
            raise ValueError(f"PDF is password-protected: {path} (use --password)")
    if len(reader.pages) == 0:
        raise ValueError(f"PDF has no pages: {path}")
    return reader


def merge_pdfs(paths, password: str = None) -> PdfWriter:
    writer = PdfWriter()
    for path in paths:
        reader = open_reader(path, password)
        # append() keeps bookmarks/outlines of each source file
        writer.append(reader, outline_item=path.stem)
    return writer


def new_job_id() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S") + "_" + uuid.uuid4().hex[:8]


def run(files, job_id: str = None, output_dir: str = "output", password: str = None) -> Path:
    if len(files) < 2:
        raise ValueError("Need at least 2 PDF files to merge")
    paths = [validate_pdf(f) for f in files]
    job_id = validate_job_id(job_id) if job_id else new_job_id()

    writer = merge_pdfs(paths, password)

    out_dir = Path(output_dir) / job_id
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "merged.pdf"
    with open(out_path, "wb") as f:
        writer.write(f)
    writer.close()
    return out_path


def main():
    parser = argparse.ArgumentParser(description="Merge 2 or more PDF files into one PDF.")
    parser.add_argument("files", nargs="*", help="PDF files to merge, in order")
    parser.add_argument("-j", "--job-id", help="Job ID (default: auto-generated)")
    parser.add_argument("-o", "--output-dir", default="output", help="Base output folder")
    parser.add_argument("-p", "--password", help="Password for encrypted input PDFs")
    args = parser.parse_args()

    files = args.files
    if not files:
        files = [input("Path to first PDF: "), input("Path to second PDF: ")]
    elif len(files) == 1:
        files.append(input("Path to second PDF: "))

    try:
        out_path = run(files, args.job_id, args.output_dir, args.password)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"Merged PDF saved to: {out_path}")


if __name__ == "__main__":
    main()
