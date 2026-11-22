# Open Merge Tool

Small command-line tools for merging files:

| Script | Merges | Output |
|---|---|---|
| [Merge_JPG.py](Merge_JPG.py) | 2 JPG images, side by side or top to bottom | `output/<job_id>/merged.jpg` |
| [Merge_PDF.py](Merge_PDF.py) | 2 or more PDFs, pages one after another | `output/<job_id>/merged.pdf` |

## Requirements

- Python 3.8+
- [Pillow](https://pypi.org/project/pillow/) (for JPG)
- [pypdf](https://pypi.org/project/pypdf/) (for PDF)

```bash
pip install -r requirements.txt
```

Opening PDFs protected with AES encryption also needs `pip install cryptography`.

## Output

Each run writes to its own folder:

```
output/<job_id>/merged.jpg
output/<job_id>/merged.pdf
```

- If you don't give a job ID, one is generated from the date, time and a random code, for example `20261122_111555_e7c13676`.
- `output/` is created in the folder you run the script from, unless you set `-o`.
- `output/` is listed in `.gitignore`, so merged files are not committed.

---

## Merge JPG

```bash
python3 Merge_JPG.py <image1.jpg> <image2.jpg> [options]
```

If you leave out the image paths, the script asks for them.

| Option | Default | Description |
|---|---|---|
| `-d`, `--direction` | `horizontal` | `horizontal` (side by side) or `vertical` (top to bottom) |
| `-j`, `--job-id` | auto | Name of the output subfolder |
| `-o`, `--output-dir` | `output` | Base output folder |
| `-q`, `--quality` | `95` | JPEG quality (1–95) |

```bash
# Side by side
python3 Merge_JPG.py photos/a.jpg photos/b.jpg

# Top to bottom, with a custom job ID
python3 Merge_JPG.py a.jpg b.jpg --direction vertical --job-id myjob
```

**How images are merged**

- **Different sizes:** the larger image is scaled down to match the smaller one, keeping its proportions (height for horizontal, width for vertical). Images are never enlarged.
- **Rotation:** photos are turned the right way up using their EXIF orientation.
- **Colour:** images are converted to RGB before merging.

**Input checks**

- Both paths must exist and be files with a `.jpg` or `.jpeg` extension.
- On any error the script prints `Error: ...` and exits with code 1.

Known gaps: the actual file content is not checked (only the extension), the quality range is not enforced, and the job ID is not sanitised, so a value like `../x` can write outside `output/`.

---

## Merge PDF

```bash
python3 Merge_PDF.py <file1.pdf> <file2.pdf> [more.pdf ...] [options]
```

Pages are added in the order the files are given. If you give no paths, the script asks for two; if you give one, it asks for the second.

| Option | Default | Description |
|---|---|---|
| `-j`, `--job-id` | auto | Name of the output subfolder |
| `-o`, `--output-dir` | `output` | Base output folder |
| `-p`, `--password` | none | Password for encrypted input PDFs (used for every input) |

```bash
# Two files
python3 Merge_PDF.py report.pdf appendix.pdf

# Three files, custom job ID
python3 Merge_PDF.py cover.pdf body.pdf back.pdf --job-id book01

# Password-protected input
python3 Merge_PDF.py a.pdf locked.pdf --password secret
```

**How PDFs are merged**

- All pages of each file are appended in order.
- Each source file becomes a bookmark (named after the file) in the merged PDF, and existing bookmarks are kept.
- Encrypted PDFs with an empty password open automatically; others need `--password`. The output is not encrypted.

**Input checks**

- At least 2 files are required, and no path may be empty.
- Each path must exist, have a `.pdf` extension, and start with a real PDF header (`%PDF-`), so renamed files are rejected.
- Files that can't be read, are locked without the right password, or have no pages are rejected.
- The job ID may only contain letters, digits, `_` and `-` (max 64 characters).
- On any error the script prints `Error: ...` and exits with code 1.

---

## Use from Python

```python
from Merge_JPG import run as merge_jpg
from Merge_PDF import run as merge_pdf

merge_jpg("a.jpg", "b.jpg", direction="vertical", job_id="job42")
merge_pdf(["a.pdf", "b.pdf", "c.pdf"], job_id="job43")
```
