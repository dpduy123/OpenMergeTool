# Merge JPG

Merge two JPG images into one JPG, side by side or top to bottom.

## Requirements

- Python 3.8+
- [Pillow](https://pypi.org/project/pillow/)

```bash
pip install pillow
```

## Usage

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

### Examples

```bash
# Side by side
python3 Merge_JPG.py photos/a.jpg photos/b.jpg

# Top to bottom, with a custom job ID
python3 Merge_JPG.py a.jpg b.jpg --direction vertical --job-id myjob
```

## Output

The result is saved as:

```
output/<job_id>/merged.jpg
```

- If you don't give a job ID, one is generated from the date, time and a random code, for example `20261122_111555_e7c13676`.
- `output/` is created in the folder you run the script from, unless you set `-o`.
- `output/` is listed in `.gitignore`, so merged images are not committed.

## How images are merged

- **Different sizes:** the larger image is scaled down to match the smaller one, keeping its proportions (height for horizontal, width for vertical). Images are never enlarged.
- **Rotation:** photos are turned the right way up using their EXIF orientation.
- **Colour:** images are converted to RGB before merging.

## Input checks

- Both paths must exist and be files.
- Both files must have a `.jpg` or `.jpeg` extension.
- On any error the script prints `Error: ...` and exits with code 1.

Known gaps: the actual file content is not checked (only the extension), the quality range is not enforced, and the job ID is not sanitised, so a value like `../x` can write outside `output/`.

## Use from Python

```python
from Merge_JPG import run

out_path = run("a.jpg", "b.jpg", direction="vertical", job_id="job42")
print(out_path)  # output/job42/merged.jpg
```
