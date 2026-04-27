# PDF OCR Scanner (Handwritten PDF Reader)

A Python tool that scans handwritten or printed PDFs using OCR (EasyOCR), extracts detected text, and optionally provides a visual preview of detected text bounding boxes.

---

## Project Status

This project is a STRICTLY PROTOTYPE.

It is not production-ready and is intended as an experimental tool.  
More features, optimization, and error handling still need to be added.

---

## Features

- Converts PDF pages into high-resolution images
- Runs OCR using EasyOCR (handwriting supported)
- Outputs detected text with confidence scores
- Prints results in a clean terminal table
- Optional GUI preview with bounding boxes drawn over text detections
- Supports scanning single PDFs or entire folders

---

## Requirements

### Install Python dependencies

```
pip install pymupdf easyocr pillow
```

### Mac (Tkinter support for preview window)

```
brew install python-tk
```

### Optional (recommended)

Use a virtual environment:

```
source venv/bin/activate
```

---

## Usage

### Scan a single PDF

```
python pdf_scraper.py file.pdf
```

### Scan with GUI preview (bounding boxes)

```
python pdf_scraper.py file.pdf --preview
```

### Scan an entire folder of PDFs

```
python pdf_scraper.py /path/to/folder
```

---

## Sample Input

A sample PDF is provided in this repository for testing the OCR pipeline.

You can run the tool using:

```
python pdf_scraper.py sample_input.pdf
```

Or with preview mode:

```
python pdf_scraper.py sample_input.pdf --preview
```

## How It Works

1. PDF pages are converted into images using PyMuPDF
2. Images are processed with EasyOCR
3. Detected text is extracted with bounding boxes and confidence scores
4. Results are printed in a structured terminal table
5. (Optional) A GUI preview shows OCR detection overlays

---

## Output Example

```
file        path                  detected text     confidence
---------------------------------------------------------------
doc.pdf     /path/doc.pdf         hello world       0.92
doc.pdf     /path/doc.pdf         test line         0.88
```

---

## GUI Preview Mode

When using `--preview`, a Tkinter window opens showing:

- PDF page rendering
- Red bounding boxes around detected text
- Text labels with confidence scores
- Navigation buttons (Prev / Next)

---

## Configuration

You can adjust OCR rendering quality:

```python
DEFAULT_DPI = 150
```

- Higher DPI = better accuracy, slower processing
- Recommended range: 100–250

---

## Project Structure

```
pdf_scraper.py   Main script (OCR + preview + CLI)
```

---

## Limitations

- OCR accuracy depends on handwriting quality
- Large PDFs may take longer to process
- Preview mode may be slow for large documents
- Non-English text requires modifying EasyOCR language settings

---

## Possible Improvements

- Export results to JSON/CSV
- Add multi-language OCR support
- Save annotated PDF output
- Add progress bar for large files
- GPU acceleration support for faster processing

---

## License

This project is intended for educational and personal use.