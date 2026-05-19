#!/usr/bin/env python3
"""
codegraph_cli.py — CLI para consultar el índice generado por build_index.py.

Subcomandos:
  search <query>     - Full-text search (FTS5) en code + docs
  symbol <name>      - Buscar definiciones de símbolos Python (class/function/_name)
  file <path>        - Listar símbolos de un archivo Python
  files <pattern>    - Listar archivos cuyo path matchea el pattern
  stats              - Mostrar estadísticas del índice

Uso típico (via wrappers en bin/):
  codegraph search "account.edi.format inheritance"
  codegraph symbol "L10nLatamDocumentType"
  codegraph file references/odoo-18.0/addons/l10n_pe/__manifest__.py
  codegraph files "*l10n_pe*"
"""

from __future__ import annotations

import argparse
import re
import sqlite3
import sys
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / ".codegraph" / "index.db"


def connect() -> sqlite3.Connection:
    if not DB_PATH.exists():
        print(
            "ERROR: index database not found at {}\n"
            "Run: python scripts/build_index.py".format(DB_PATH),
            file=sys.stderr,
        )
        sys.exit(2)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def cmd_search(args: argparse.Namespace) -> int:
    conn = connect()
    cur = conn.cursor()
    # FTS5 chokes on unquoted dots, dashes, etc. Auto-quote terms that contain
    # any non-word character (except FTS5 operators AND/OR/NEAR/NOT or already-quoted).
    raw = args.query.strip()
    if raw.startswith('"') and raw.endswith('"'):
        fts_query = raw
    else:
        # Tokenize on whitespace, quote each token that has non-word chars
        operators = {"AND", "OR", "NOT", "NEAR"}
        parts = []
        for tok in raw.split():
            if tok.upper() in operators or tok in ("(", ")"):
                parts.append(tok)
            elif re.search(r"[^\w]", tok):
                parts.append(f'"{tok}"')
            else:
                parts.append(tok)
        fts_query = " ".join(parts)
    sql = """
        SELECT
            documents.path AS path,
            documents.kind AS kind,
            snippet(documents, 2, '[33m', '[0m', '...', 8) AS snippet,
            rank
        FROM documents
        WHERE documents MATCH ?
        ORDER BY rank
        LIMIT ?
    """
    try:
        rows = cur.execute(sql, (fts_query, args.limit)).fetchall()
    except sqlite3.OperationalError as e:
        print(f"FTS5 error: {e}", file=sys.stderr)
        print("Hint: quote phrases con comillas dobles, ej: \"account.edi.format\"", file=sys.stderr)
        return 2

    if not rows:
        print(f"No results for: {fts_query}")
        return 0

    for r in rows:
        kind_tag = f"[{r['kind']}]".ljust(10)
        print(f"\n{kind_tag} {r['path']}")
        snippet = r["snippet"].replace("\n", " ").strip()
        print(f"  {snippet}")
    print(f"\n({len(rows)} results)")
    return 0


def cmd_symbol(args: argparse.Namespace) -> int:
    conn = connect()
    cur = conn.cursor()
    # Búsqueda exacta o LIKE
    if args.exact:
        rows = cur.execute(
            """
            SELECT s.name, s.kind, s.line, s.col, s.signature, s.parent, f.path
            FROM symbols s
            JOIN files f ON s.file_id = f.id
            WHERE s.name = ?
            ORDER BY f.path, s.line
            LIMIT ?
            """,
            (args.name, args.limit),
        ).fetchall()
    else:
        rows = cur.execute(
            """
            SELECT s.name, s.kind, s.line, s.col, s.signature, s.parent, f.path
            FROM symbols s
            JOIN files f ON s.file_id = f.id
            WHERE s.name LIKE ?
            ORDER BY (s.name = ?) DESC, f.path, s.line
            LIMIT ?
            """,
            (f"%{args.name}%", args.name, args.limit),
        ).fetchall()

    if not rows:
        print(f"No symbol matches: {args.name}")
        return 0

    for r in rows:
        parent = f" (in {r['parent']})" if r["parent"] else ""
        print(f"{r['path']}:{r['line']}:{r['col']}  [{r['kind']}]  {r['signature']}{parent}")
    print(f"\n({len(rows)} matches)")
    return 0


def cmd_file(args: argparse.Namespace) -> int:
    conn = connect()
    cur = conn.cursor()
    row = cur.execute(
        "SELECT id, path, kind, size FROM files WHERE path = ?", (args.path,)
    ).fetchone()
    if not row:
        # Try relative match
        row = cur.execute(
            "SELECT id, path, kind, size FROM files WHERE path LIKE ? LIMIT 1",
            (f"%{args.path}",),
        ).fetchone()
    if not row:
        print(f"File not in index: {args.path}", file=sys.stderr)
        return 1

    print(f"# {row['path']}  [{row['kind']}, {row['size']} bytes]\n")
    syms = cur.execute(
        "SELECT name, kind, line, signature, parent FROM symbols"
        " WHERE file_id = ? ORDER BY line",
        (row["id"],),
    ).fetchall()
    if not syms:
        print("(no extracted symbols — likely XML/CSV/non-Python file)")
        return 0
    for s in syms:
        indent = "  " if s["parent"] else ""
        parent = f" -- in {s['parent']}" if s["parent"] else ""
        print(f"{indent}{s['line']:5d}  [{s['kind']}]  {s['signature']}{parent}")
    return 0


def cmd_files(args: argparse.Namespace) -> int:
    conn = connect()
    cur = conn.cursor()
    pattern = args.pattern.replace("*", "%")
    rows = cur.execute(
        "SELECT path, kind, size FROM files WHERE path LIKE ? ORDER BY path LIMIT ?",
        (pattern, args.limit),
    ).fetchall()
    if not rows:
        print(f"No files match: {args.pattern}")
        return 0
    for r in rows:
        print(f"{r['kind']:9}  {r['size']:8d}  {r['path']}")
    print(f"\n({len(rows)} files)")
    return 0


def cmd_stats(args: argparse.Namespace) -> int:
    conn = connect()
    cur = conn.cursor()
    print(f"Index at: {DB_PATH}")
    print(f"DB size:  {DB_PATH.stat().st_size // 1024} KB\n")
    files = cur.execute("SELECT COUNT(*) FROM files").fetchone()[0]
    syms = cur.execute("SELECT COUNT(*) FROM symbols").fetchone()[0]
    print(f"Files: {files}")
    print(f"Symbols: {syms}\n")
    print("Files by kind:")
    for kind, count in cur.execute("SELECT kind, COUNT(*) FROM files GROUP BY kind ORDER BY 2 DESC"):
        print(f"  {kind:10}  {count}")
    print("\nSymbols by kind:")
    for kind, count in cur.execute("SELECT kind, COUNT(*) FROM symbols GROUP BY kind ORDER BY 2 DESC"):
        print(f"  {kind:12}  {count}")
    print("\nMetadata:")
    for k, v in cur.execute("SELECT key, value FROM metadata"):
        print(f"  {k}: {v}")
    return 0


def main() -> int:
    p = argparse.ArgumentParser(prog="codegraph", description="Query l10n-paraguay code/docs index.")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("search", help="Full-text search across code + docs")
    s.add_argument("query")
    s.add_argument("--limit", type=int, default=20)
    s.set_defaults(fn=cmd_search)

    s = sub.add_parser("symbol", help="Find Python symbol definitions")
    s.add_argument("name")
    s.add_argument("--exact", action="store_true", help="Match exact name (default: substring)")
    s.add_argument("--limit", type=int, default=30)
    s.set_defaults(fn=cmd_symbol)

    s = sub.add_parser("file", help="List symbols in a file")
    s.add_argument("path")
    s.set_defaults(fn=cmd_file)

    s = sub.add_parser("files", help="List files matching a glob pattern")
    s.add_argument("pattern", help="Glob-style: l10n_pe* or %%l10n_pe%%")
    s.add_argument("--limit", type=int, default=100)
    s.set_defaults(fn=cmd_files)

    s = sub.add_parser("stats", help="Show index statistics")
    s.set_defaults(fn=cmd_stats)

    args = p.parse_args()
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
