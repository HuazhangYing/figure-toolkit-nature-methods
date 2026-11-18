"""Technical QC for Nature Methods-oriented figure exports.

Checks file presence/readability, PDF page dimensions, font embedding when Poppler
is installed, SVG text nodes, PNG DPI metadata (when Pillow is installed), and size.
It cannot validate statistical design, data provenance, or scientific interpretation.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

MM_PER_PT = 25.4 / 72.0
MAX_WIDTH_MM = 180.0
MAX_HEIGHT_MM = 170.0
MAX_FILE_MB = 50.0

def run_cmd(args):
    try:
        return subprocess.run(args, capture_output=True, text=True, check=False)
    except Exception:
        return None

def pdf_dimensions(path: Path):
    if shutil.which("pdfinfo"):
        result = run_cmd(["pdfinfo", str(path)])
        if result and result.returncode == 0:
            page = re.search(r"Page size:\s*([\d.]+)\s+x\s+([\d.]+)\s+pts", result.stdout)
            if page:
                return float(page.group(1)) * MM_PER_PT, float(page.group(2)) * MM_PER_PT
    raw = path.read_bytes()
    match = re.search(rb"/MediaBox\s*\[\s*([-0-9.]+)\s+([-0-9.]+)\s+([-0-9.]+)\s+([-0-9.]+)\s*\]", raw)
    if match:
        x0, y0, x1, y1 = [float(x) for x in match.groups()]
        return (x1 - x0) * MM_PER_PT, (y1 - y0) * MM_PER_PT
    return None

def inspect_pdf(path: Path):
    item = {"file": str(path), "format": "pdf", "checks": [], "warnings": [], "errors": []}
    if not path.exists() or path.stat().st_size == 0:
        item["errors"].append("Missing or empty PDF.")
        return item
    dims = pdf_dimensions(path)
    if dims:
        w, h = dims
        item["dimensions_mm"] = {"width": round(w, 2), "height": round(h, 2)}
        if w > MAX_WIDTH_MM + 0.2:
            item["errors"].append(f"Width {w:.2f} mm exceeds {MAX_WIDTH_MM:.0f} mm.")
        if h > MAX_HEIGHT_MM + 0.2:
            item["errors"].append(f"Height {h:.2f} mm exceeds {MAX_HEIGHT_MM:.0f} mm.")
        item["checks"].append("PDF page dimensions read.")
    else:
        item["warnings"].append("Could not read PDF page dimensions; install Poppler (pdfinfo) or pypdf for manual inspection.")
    if shutil.which("pdffonts"):
        result = run_cmd(["pdffonts", str(path)])
        if result and result.returncode == 0:
            rows = [line for line in result.stdout.splitlines() if line.strip()]
            font_rows = [line for line in rows if re.search(r"\s(yes|no)\s+(yes|no)\s+(yes|no)\s+\d+\s+\d+$", line)]
            if font_rows:
                not_embedded = [line for line in font_rows if re.search(r"\sno\s+(yes|no)\s+(yes|no)\s+\d+\s+\d+$", line)]
                if not_embedded:
                    item["warnings"].append("One or more PDF fonts may not be embedded; inspect pdffonts output.")
                else:
                    item["checks"].append("PDF font embedding reported by pdffonts.")
                item["fonts"] = font_rows
            else:
                item["warnings"].append("No font rows detected by pdffonts; inspect PDF manually.")
        else:
            item["warnings"].append("pdffonts could not inspect the PDF.")
    else:
        item["warnings"].append("Poppler pdffonts unavailable; font embedding was not checked.")
    return item

def inspect_svg(path: Path):
    item = {"file": str(path), "format": "svg", "checks": [], "warnings": [], "errors": []}
    if not path.exists() or path.stat().st_size == 0:
        item["errors"].append("Missing or empty SVG.")
        return item
    raw = path.read_text(encoding="utf-8", errors="replace")
    if "<svg" not in raw:
        item["errors"].append("No SVG root element found.")
    else:
        item["checks"].append("SVG root element found.")
    text_count = len(re.findall(r"<text(?:\s|>)", raw))
    item["text_elements"] = text_count
    if text_count == 0:
        item["warnings"].append("No SVG text elements detected. Text may be outlined, or the figure may contain no text.")
    else:
        item["checks"].append(f"{text_count} editable SVG text element(s) detected.")
    return item

def inspect_png(path: Path):
    item = {"file": str(path), "format": "png", "checks": [], "warnings": [], "errors": []}
    try:
        from PIL import Image
        with Image.open(path) as im:
            item["pixel_size"] = {"width": im.width, "height": im.height}
            dpi = im.info.get("dpi")
            if dpi:
                item["dpi"] = [round(float(dpi[0]), 1), round(float(dpi[1]), 1)]
                item["checks"].append("PNG DPI metadata found.")
            else:
                item["warnings"].append("PNG has no DPI metadata.")
    except ImportError:
        item["warnings"].append("Pillow unavailable; PNG dimensions/DPI not checked.")
    except Exception as exc:
        item["errors"].append(f"Could not read PNG: {exc}")
    item["warnings"].append("PNG is a preview format in this toolkit, not the preferred Nature Methods main-figure upload.")
    return item

def inspect_file(path: Path):
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        item = inspect_pdf(path)
    elif suffix == ".svg":
        item = inspect_svg(path)
    elif suffix == ".png":
        item = inspect_png(path)
    else:
        item = {"file": str(path), "format": suffix.lstrip("."), "checks": [], "warnings": [], "errors": []}
    if path.exists():
        size_mb = path.stat().st_size / (1024 * 1024)
        item["size_mb"] = round(size_mb, 2)
        if size_mb > MAX_FILE_MB:
            item["warnings"].append(f"File exceeds {MAX_FILE_MB:.0f} MB.")
    return item

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", help="A figure file or directory containing PDF/SVG/PNG exports.")
    parser.add_argument("--strict", action="store_true", help="Return non-zero if any technical errors are present; optional-tool warnings remain informational.")
    parser.add_argument("--report", default=None, help="Optional JSON report path.")
    args = parser.parse_args()

    target = Path(args.path)
    if target.is_dir():
        files = sorted(p for p in target.iterdir() if p.suffix.lower() in {".pdf", ".svg", ".png"})
    elif target.is_file():
        files = [target]
    else:
        print(f"Path not found: {target}", file=sys.stderr)
        return 2

    results = [inspect_file(p) for p in files]
    report = {
        "profile": "Nature Methods",
        "max_width_mm": MAX_WIDTH_MM,
        "max_height_mm": MAX_HEIGHT_MM,
        "files_checked": len(results),
        "results": results,
        "scope_limit": "Technical checks only; statistical correctness and scientific integrity require human review."
    }
    report_path = Path(args.report) if args.report else (target / "figure_qc_report.json" if target.is_dir() else target.with_suffix(".qc.json"))
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    for item in results:
        print(f"\n{item['file']}")
        for msg in item.get("checks", []):
            print(f"  PASS: {msg}")
        for msg in item.get("warnings", []):
            print(f"  WARN: {msg}")
        for msg in item.get("errors", []):
            print(f"  ERROR: {msg}")
    errors = sum(len(x.get("errors", [])) for x in results)
    warnings = sum(len(x.get("warnings", [])) for x in results)
    print(f"\nQC summary: {len(results)} file(s), {errors} error(s), {warnings} warning(s).")
    print(f"JSON report: {report_path}")
    if errors:
        return 1
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
