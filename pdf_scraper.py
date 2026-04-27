"""
pdf_scraper.py — Scan handwritten PDFs and preview OCR detections.

Dependencies:
    pip install pymupdf easyocr pillow
    brew install python-tk  (Mac only)
    source venv/bin/activate

Usage:
    python pdf_scraper.py file.pdf
    python pdf_scraper.py file.pdf --preview
    python pdf_scraper.py /some/folder
"""

import argparse
import io
import sys
import time
from pathlib import Path

import easyocr
import fitz
import tkinter as tk
from PIL import Image, ImageDraw, ImageTk


# Keep between 100-250. Higher = better accuracy but slower.
DEFAULT_DPI = 150


def pdf_to_images(path: Path, dpi: int) -> list[bytes]:
    doc = fitz.open(str(path))
    scale = fitz.Matrix(dpi / 72, dpi / 72)
    images = []

    for page in doc:
        png_bytes = page.get_pixmap(matrix=scale, colorspace=fitz.csRGB).tobytes("png")
        images.append(png_bytes)

    doc.close()
    return images


def run_ocr(images: list[bytes], reader: easyocr.Reader) -> list[tuple]:
    segments = []

    for i, img in enumerate(images, start=1):
        print(f"    page {i}/{len(images)}...", end="\r")
        detections = reader.readtext(img, detail=1, paragraph=False)

        for bbox, text, confidence in detections:
            clean_text = text.strip()
            rounded_conf = round(confidence, 4)
            segments.append((clean_text, rounded_conf, bbox))

    print(" " * 30, end="\r")
    return segments


def print_table(results: list[dict]):
    flat_rows = []
    for result in results:
        if result["segments"]:
            for text, conf, _ in result["segments"]:
                row = (result["file"], result["path"], text, str(conf))
                flat_rows.append(row)
        else:
            row = (result["file"], result["path"], "—", "—")
            flat_rows.append(row)

    headers = ("file", "path", "detected text", "confidence")

    col_widths = []
    for col_index in range(4):
        widest_value = max(len(row[col_index]) for row in flat_rows)
        col_width = max(len(headers[col_index]), widest_value)
        col_widths.append(col_width)

    def format_row(a, b, c, d):
        return (
            f"| {a:<{col_widths[0]}} "
            f"| {b:<{col_widths[1]}} "
            f"| {c:<{col_widths[2]}} "
            f"| {d:<{col_widths[3]}} |"
        )

    divider = (
        f"+-{'-' * col_widths[0]}-"
        f"+-{'-' * col_widths[1]}-"
        f"+-{'-' * col_widths[2]}-"
        f"+-{'-' * col_widths[3]}-+"
    )

    print(f"\n{divider}")
    print(format_row(*headers))
    print(divider)
    for row in flat_rows:
        print(format_row(*row))
    print(f"{divider}\n")


def show_preview(images: list[bytes], segments: list[tuple]):
    root = tk.Tk()
    root.title("OCR Preview — what the program sees")

    canvas = tk.Canvas(root, bg="gray20")
    canvas.pack(fill=tk.BOTH, expand=True)

    page_label = tk.Label(root, bg="gray20", fg="white", font=("Helvetica", 12))
    page_label.pack()

    nav_bar = tk.Frame(root, bg="gray20")
    nav_bar.pack(pady=6)

    current_page = [0]
    # List instead of a plain variable so draw_page can mutate it from inside a closure
    photo_ref = []

    def draw_page(index):
        img = Image.open(io.BytesIO(images[index])).convert("RGB")
        draw = ImageDraw.Draw(img)

        for text, conf, bbox in segments:
            xs = [point[0] for point in bbox]
            ys = [point[1] for point in bbox]
            x0, y0, x1, y1 = min(xs), min(ys), max(xs), max(ys)
            draw.rectangle([x0, y0, x1, y1], outline="red", width=3)
            draw.text((x0, max(y0 - 18, 0)), f"{text} ({conf})", fill="red")

        if img.width > 900:
            scale = 900 / img.width
            new_size = (900, int(img.height * scale))
            img = img.resize(new_size, Image.LANCZOS)

        photo = ImageTk.PhotoImage(img)
        photo_ref[:] = [photo]

        canvas.config(width=img.width, height=img.height)
        canvas.create_image(0, 0, anchor=tk.NW, image=photo)
        page_label.config(text=f"Page {index + 1} of {len(images)}")

    def go_prev():
        if current_page[0] > 0:
            current_page[0] -= 1
            draw_page(current_page[0])

    def go_next():
        if current_page[0] < len(images) - 1:
            current_page[0] += 1
            draw_page(current_page[0])

    tk.Button(nav_bar, text="◀ Prev", width=10, command=go_prev).pack(side=tk.LEFT, padx=4)
    tk.Button(nav_bar, text="Next ▶", width=10, command=go_next).pack(side=tk.LEFT, padx=4)
    tk.Button(nav_bar, text="Close",  width=10, command=root.destroy).pack(side=tk.LEFT, padx=4)

    draw_page(0)
    root.mainloop()


def resolve_pdf_paths(inputs: list[str]) -> list[Path]:
    paths = []
    for p in inputs:
        path = Path(p)
        if path.is_dir():
            paths.extend(sorted(path.glob("*.pdf")))
        elif path.suffix.lower() == ".pdf":
            paths.append(path)
        else:
            print(f"Skipping (not a PDF): {p}")

    return paths


def main():
    parser = argparse.ArgumentParser(description="Scan handwritten PDFs with OCR.")
    parser.add_argument("pdfs", nargs="*", help="PDF files or folders to scan.")
    parser.add_argument("--dpi", type=int, default=DEFAULT_DPI, help="Render resolution (default: 150).")
    parser.add_argument("--preview", action="store_true", help="Open GUI preview with OCR boxes drawn.")
    args = parser.parse_args()

    if args.pdfs:
        inputs = args.pdfs
    else:
        inputs = ["."]

    pdf_files = resolve_pdf_paths(inputs)

    if not pdf_files:
        sys.exit("No PDF files found.")

    print("\nLoading EasyOCR...")
    reader = easyocr.Reader(["en"], gpu=False)

    results = []
    for pdf_path in pdf_files:
        print(f"\nScanning: {pdf_path.name}")
        start = time.time()

        images = pdf_to_images(pdf_path, args.dpi)
        segments = run_ocr(images, reader)

        elapsed = round(time.time() - start, 1)
        print(f"  Done in {elapsed}s — {len(segments)} segment(s) detected")

        results.append({
            "file": pdf_path.name,
            "path": str(pdf_path.resolve()),
            "segments": segments,
        })

    # Table prints first so the preview window doesn't block the output
    print_table(results)

    if args.preview:
        for result in results:
            pdf_images = pdf_to_images(Path(result["path"]), args.dpi)
            show_preview(pdf_images, result["segments"])


if __name__ == "__main__":
    main()