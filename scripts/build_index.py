#!/usr/bin/env python3
"""
build_index.py — Construye el índice de búsqueda de l10n-paraguay.

Indexa:
  - references/**/*.{py,xml,csv,rst,po,pot,md}  (código de referencia)
  - docs/**/*.md                                 (documentación curada)

Almacena en .codegraph/index.db (SQLite con FTS5).

Tablas:
  - documents(id, path, kind, mtime, size, content)        — full-text via FTS5
  - symbols(id, file_id, name, kind, line, col, signature) — extraído via ast
                                                             (solo .py)

CLI:
  python scripts/build_index.py            # rebuild full
  python scripts/build_index.py --stats    # mostrar contadores sin reindexar

Uso típico desde el CLI codegraph:
  bin/codegraph search "query"
  bin/codegraph symbol "name"
  bin/codegraph file "path"

Requisitos: Python 3.11+. Sin dependencias externas (todo stdlib).
"""

from __future__ import annotations

import argparse
import ast
import os
import sqlite3
import sys
import time
from pathlib import Path
from typing import Iterable, Optional

# ---------------------------------------------------------------------------
# Paths / config
# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = REPO_ROOT / ".codegraph" / "index.db"

# Carpetas indexables (relativas a REPO_ROOT)
INCLUDE_DIRS = [
    "references",
    "docs",
]

# Extensiones que se indexan + tipo lógico
EXT_KIND = {
    ".py": "python",
    ".xml": "xml",
    ".csv": "csv",
    ".rst": "rst",
    ".po": "po",
    ".pot": "po",
    ".md": "markdown",
}

# Patrones de exclusión (substring match en path)
EXCLUDE_PATTERNS = [
    "/.git/",
    "/node_modules/",
    "/__pycache__/",
    "/.pytest_cache/",
    "/.mypy_cache/",
    "/.ruff_cache/",
    "/.tox/",
    "/htmlcov/",
    "/dist/",
    "/build/",
    "/.codegraph/",
    "/i18n/",          # .pot/.po los indexamos pero NO los .mo
]

# Tamaño máximo de un archivo a indexar (8 MB)
MAX_FILE_SIZE = 8 * 1024 * 1024

# ---------------------------------------------------------------------------
# Schema
# ---------------------------------------------------------------------------
SCHEMA = """
CREATE TABLE IF NOT EXISTS files (
    id INTEGER PRIMARY KEY,
    path TEXT UNIQUE NOT NULL,
    kind TEXT NOT NULL,
    mtime REAL NOT NULL,
    size INTEGER NOT NULL
);

CREATE INDEX IF NOT EXISTS files_kind_idx ON files(kind);
CREATE INDEX IF NOT EXISTS files_path_idx ON files(path);

-- Full-text index. content_rowid se alinea con files.id (1:1).
CREATE VIRTUAL TABLE IF NOT EXISTS documents USING fts5(
    path UNINDEXED,
    kind UNINDEXED,
    content,
    tokenize = 'porter unicode61 remove_diacritics 2'
);

CREATE TABLE IF NOT EXISTS symbols (
    id INTEGER PRIMARY KEY,
    file_id INTEGER NOT NULL REFERENCES files(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    kind TEXT NOT NULL,         -- 'class' | 'function' | 'method' | 'odoo_model'
    line INTEGER NOT NULL,
    col INTEGER NOT NULL,
    signature TEXT,
    parent TEXT                 -- nombre del símbolo contenedor (clase, etc.)
);

CREATE INDEX IF NOT EXISTS symbols_name_idx ON symbols(name);
CREATE INDEX IF NOT EXISTS symbols_kind_idx ON symbols(kind);
CREATE INDEX IF NOT EXISTS symbols_file_idx ON symbols(file_id);

CREATE TABLE IF NOT EXISTS metadata (
    key TEXT PRIMARY KEY,
    value TEXT
);
"""

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def is_excluded(path: str) -> bool:
    p = path.replace("\\", "/")
    return any(pat in p for pat in EXCLUDE_PATTERNS)


def iter_indexable_files(root: Path) -> Iterable[Path]:
    for incl in INCLUDE_DIRS:
        base = root / incl
        if not base.exists():
            continue
        for path in base.rglob("*"):
            if not path.is_file():
                continue
            if path.suffix.lower() not in EXT_KIND:
                continue
            if is_excluded(str(path)):
                continue
            try:
                if path.stat().st_size > MAX_FILE_SIZE:
                    continue
            except OSError:
                continue
            yield path


def read_safe(path: Path) -> Optional[str]:
    """Lee con tolerancia a encoding errors."""
    for enc in ("utf-8", "latin-1"):
        try:
            return path.read_text(encoding=enc, errors="replace")
        except OSError:
            return None
    return None


def extract_python_symbols(content: str, file_id: int) -> list[tuple]:
    """Extrae clases, funciones, métodos y `_name = 'model.x'` de un módulo Python.

    Devuelve lista de tuplas (file_id, name, kind, line, col, signature, parent).
    """
    out: list[tuple] = []
    try:
        tree = ast.parse(content)
    except SyntaxError:
        return out

    def visit(node, parent: Optional[str] = None) -> None:
        if isinstance(node, ast.ClassDef):
            base_names = [
                _name_of(b)
                for b in node.bases
                if _name_of(b)
            ]
            sig = f"class {node.name}({', '.join(base_names)})" if base_names else f"class {node.name}"
            out.append((file_id, node.name, "class", node.lineno, node.col_offset, sig, parent))
            for child in node.body:
                if isinstance(child, ast.Assign):
                    for tgt in child.targets:
                        if (
                            isinstance(tgt, ast.Name)
                            and tgt.id in ("_name", "_inherit")
                            and isinstance(child.value, ast.Constant)
                            and isinstance(child.value.value, str)
                        ):
                            out.append((
                                file_id,
                                child.value.value,
                                "odoo_model",
                                child.lineno,
                                child.col_offset,
                                f"{tgt.id} = {child.value.value!r}",
                                node.name,
                            ))
                visit(child, parent=node.name)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            kind = "method" if parent else "function"
            args = ", ".join(a.arg for a in node.args.args)
            sig = f"def {node.name}({args})"
            out.append((file_id, node.name, kind, node.lineno, node.col_offset, sig, parent))
            for child in node.body:
                visit(child, parent=node.name)
        else:
            for child in ast.iter_child_nodes(node):
                visit(child, parent=parent)

    visit(tree)
    return out


def _name_of(node: ast.AST) -> Optional[str]:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        base = _name_of(node.value)
        return f"{base}.{node.attr}" if base else node.attr
    return None


# ---------------------------------------------------------------------------
# Index builder
# ---------------------------------------------------------------------------
def build_index() -> dict:
    """Construye/reconstruye el índice completo."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    if DB_PATH.exists():
        DB_PATH.unlink()

    conn = sqlite3.connect(DB_PATH)
    conn.executescript(SCHEMA)
    conn.execute("PRAGMA journal_mode = WAL")
    conn.execute("PRAGMA synchronous = NORMAL")
    cur = conn.cursor()

    stats = {"files": 0, "by_kind": {}, "symbols": 0, "started_at": time.time()}

    for path in iter_indexable_files(REPO_ROOT):
        kind = EXT_KIND[path.suffix.lower()]
        content = read_safe(path)
        if content is None:
            continue
        rel = str(path.relative_to(REPO_ROOT)).replace("\\", "/")
        try:
            st = path.stat()
        except OSError:
            continue

        cur.execute(
            "INSERT INTO files(path, kind, mtime, size) VALUES (?, ?, ?, ?)",
            (rel, kind, st.st_mtime, st.st_size),
        )
        file_id = cur.lastrowid
        cur.execute(
            "INSERT INTO documents(rowid, path, kind, content) VALUES (?, ?, ?, ?)",
            (file_id, rel, kind, content),
        )
        if kind == "python":
            syms = extract_python_symbols(content, file_id)
            if syms:
                cur.executemany(
                    "INSERT INTO symbols(file_id, name, kind, line, col, signature, parent)"
                    " VALUES (?, ?, ?, ?, ?, ?, ?)",
                    syms,
                )
                stats["symbols"] += len(syms)

        stats["files"] += 1
        stats["by_kind"][kind] = stats["by_kind"].get(kind, 0) + 1

        if stats["files"] % 500 == 0:
            conn.commit()
            print(f"  ... {stats['files']} files indexed", file=sys.stderr)

    cur.executemany(
        "INSERT INTO metadata(key, value) VALUES (?, ?)",
        [
            ("indexed_at", str(time.time())),
            ("repo_root", str(REPO_ROOT)),
            ("files", str(stats["files"])),
            ("symbols", str(stats["symbols"])),
        ],
    )
    conn.commit()
    conn.execute("VACUUM")
    conn.close()

    stats["duration_s"] = round(time.time() - stats["started_at"], 1)
    return stats


def show_stats() -> dict:
    if not DB_PATH.exists():
        return {"error": "Index not built yet. Run: python scripts/build_index.py"}
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    files = cur.execute("SELECT COUNT(*) FROM files").fetchone()[0]
    syms = cur.execute("SELECT COUNT(*) FROM symbols").fetchone()[0]
    by_kind = dict(cur.execute("SELECT kind, COUNT(*) FROM files GROUP BY kind").fetchall())
    sym_by_kind = dict(cur.execute("SELECT kind, COUNT(*) FROM symbols GROUP BY kind").fetchall())
    meta = dict(cur.execute("SELECT key, value FROM metadata").fetchall())
    conn.close()
    return {
        "files": files,
        "symbols": syms,
        "files_by_kind": by_kind,
        "symbols_by_kind": sym_by_kind,
        "metadata": meta,
    }


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------
def main() -> int:
    parser = argparse.ArgumentParser(description="Build l10n-paraguay search index.")
    parser.add_argument("--stats", action="store_true", help="Show current index stats and exit")
    args = parser.parse_args()

    if args.stats:
        stats = show_stats()
        for k, v in stats.items():
            print(f"{k}: {v}")
        return 0

    print(f"Building index at {DB_PATH} ...", file=sys.stderr)
    print(f"  Repo root: {REPO_ROOT}", file=sys.stderr)
    print(f"  Include dirs: {INCLUDE_DIRS}", file=sys.stderr)
    stats = build_index()
    print("", file=sys.stderr)
    print("=== INDEX BUILD COMPLETE ===", file=sys.stderr)
    print(f"  Total files: {stats['files']}", file=sys.stderr)
    for kind, count in sorted(stats["by_kind"].items()):
        print(f"    {kind}: {count}", file=sys.stderr)
    print(f"  Total Python symbols: {stats['symbols']}", file=sys.stderr)
    print(f"  Duration: {stats['duration_s']}s", file=sys.stderr)
    print(f"  Database: {DB_PATH} ({DB_PATH.stat().st_size // 1024} KB)", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
