"""Extrae texto de un PDF por rango de páginas usando pypdf.

Uso:
    python scripts/extract_pdf.py <pdf_path> [start_page] [end_page]
    python scripts/extract_pdf.py <pdf_path> search <pattern>

Páginas 1-indexed (humanas). `search` busca un patrón case-insensitive y
reporta números de página donde aparece.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

from pypdf import PdfReader


def extract_range(pdf_path: Path, start: int, end: int) -> None:
    reader = PdfReader(str(pdf_path))
    total = len(reader.pages)
    start = max(1, start)
    end = min(total, end)
    print(f"=== {pdf_path.name} — pages {start}-{end} of {total} ===")
    for i in range(start - 1, end):
        page = reader.pages[i]
        text = page.extract_text() or ""
        print(f"\n--- PAGE {i + 1} ---\n{text}")


def search(pdf_path: Path, pattern: str) -> None:
    reader = PdfReader(str(pdf_path))
    rx = re.compile(pattern, re.IGNORECASE)
    print(f"=== Search '{pattern}' in {pdf_path.name} ({len(reader.pages)} pages) ===")
    hits = 0
    for i, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        if rx.search(text):
            hits += 1
            snippets = []
            for m in rx.finditer(text):
                a = max(0, m.start() - 50)
                b = min(len(text), m.end() + 50)
                snippets.append(text[a:b].replace("\n", " "))
            print(f"\nPAGE {i}: {len(snippets)} hit(s)")
            for s in snippets[:3]:
                print(f"  ... {s} ...")
    print(f"\nTotal pages with matches: {hits}")


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 1
    pdf_path = Path(sys.argv[1])
    if not pdf_path.exists():
        print(f"ERROR: {pdf_path} not found")
        return 1
    if len(sys.argv) >= 3 and sys.argv[2] == "search":
        search(pdf_path, sys.argv[3])
        return 0
    start = int(sys.argv[2]) if len(sys.argv) >= 3 else 1
    end = int(sys.argv[3]) if len(sys.argv) >= 4 else start + 9
    extract_range(pdf_path, start, end)
    return 0


if __name__ == "__main__":
    sys.exit(main())
