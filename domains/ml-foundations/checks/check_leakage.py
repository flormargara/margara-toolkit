#!/usr/bin/env python3
"""Detecta columnas prohibidas (leakage) en código o en una lista de features.

Usos:
  check_leakage.py --features features.txt          lista final de features, una por línea
  check_leakage.py src/modelo.py notebooks/fe.ipynb  escanea código (.py, .sql, .ipynb)
  check_leakage.py --hook                            modo hook: lee JSON por stdin
                                                     (Claude Code / Cursor) y escanea el
                                                     archivo editado

Patrones: --patterns <archivo>, o forbidden_columns.txt en la raíz del proyecto,
o el ejemplo genérico de este directorio como último recurso (cada dominio
tiene su propia lista de ejemplo, por ejemplo domains/credit-scoring/checks/).

Salida: 0 sin hallazgos; 1 con hallazgos; en modo hook, 2 con hallazgos (el
agente recibe el mensaje por stderr y debe corregir o justificar).

Una línea de código con el comentario "leakage-ok" se ignora (uso legítimo,
por ejemplo al construir el target).

Solo usa la biblioteca estándar, a propósito: tiene que correr en cualquier entorno.
"""

from __future__ import annotations

import argparse
import fnmatch
import json
import os
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXAMPLE_PATTERNS = HERE / "forbidden_columns.example.txt"
CODE_SUFFIXES = {".py", ".sql", ".ipynb"}
ALLOW_MARKER = "leakage-ok"


def find_patterns_file(explicit: str | None, project_dir: Path) -> Path:
    if explicit:
        return Path(explicit)
    candidate = project_dir / "forbidden_columns.txt"
    if candidate.exists():
        return candidate
    return EXAMPLE_PATTERNS


def load_patterns(path: Path) -> list[re.Pattern[str]]:
    patterns = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if line and not line.startswith("#"):
            patterns.append(re.compile(line, re.IGNORECASE))
    return patterns


def code_lines(path: Path) -> list[tuple[int, str]]:
    """Devuelve (número de línea, texto). En notebooks, solo celdas de código."""
    if path.suffix == ".ipynb":
        nb = json.loads(path.read_text(encoding="utf-8"))
        lines: list[tuple[int, str]] = []
        for cell_no, cell in enumerate(nb.get("cells", []), start=1):
            if cell.get("cell_type") != "code":
                continue
            source = cell.get("source", [])
            text = "".join(source) if isinstance(source, list) else source
            for line_no, line in enumerate(text.splitlines(), start=1):
                # Codifica celda y línea en un solo número legible: 3001 = celda 3, línea 1
                lines.append((cell_no * 1000 + line_no, line))
        return lines
    text = path.read_text(encoding="utf-8", errors="replace")
    return list(enumerate(text.splitlines(), start=1))


def scan_lines(lines, patterns, allow_marker=True):
    findings = []
    for line_no, line in lines:
        if allow_marker and ALLOW_MARKER in line:
            continue
        for pat in patterns:
            match = pat.search(line)
            if match:
                findings.append((line_no, match.group(0), line.strip()))
                break
    return findings


def format_location(path: Path, line_no: int) -> str:
    if path.suffix == ".ipynb":
        return f"{path}:celda {line_no // 1000}, línea {line_no % 1000}"
    return f"{path}:{line_no}"


def scan_features(path: Path, patterns) -> list[str]:
    out = []
    for line_no, name in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        name = name.strip()
        if not name or name.startswith("#"):
            continue
        for pat in patterns:
            if pat.search(name):
                out.append(f"{path}:{line_no}: feature prohibida '{name}' (patrón {pat.pattern})")
                break
    return out


def scan_code_files(paths: list[Path], patterns) -> list[str]:
    out = []
    for path in paths:
        if path.suffix not in CODE_SUFFIXES or not path.exists():
            continue
        for line_no, token, line in scan_lines(code_lines(path), patterns):
            out.append(f"{format_location(path, line_no)}: '{token}' en: {line[:120]}")
    return out


def hook_target(include: list[str]) -> tuple[Path | None, Path]:
    """Lee el JSON del hook y devuelve (archivo editado, raíz del proyecto)."""
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        return None, Path.cwd()
    tool_input = payload.get("tool_input") or {}
    file_path = tool_input.get("file_path") or tool_input.get("notebook_path") or payload.get("file_path")
    project_dir = Path(os.environ.get("CLAUDE_PROJECT_DIR") or payload.get("cwd") or Path.cwd())
    if not file_path:
        return None, project_dir
    path = Path(file_path)
    if include:
        try:
            rel = str(path.resolve().relative_to(project_dir.resolve()))
        except ValueError:
            rel = str(path)
        if not any(fnmatch.fnmatch(rel, pattern) for pattern in include):
            return None, project_dir
    return path, project_dir


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("files", nargs="*", help="Archivos de código a escanear")
    parser.add_argument("--features", help="Archivo con la lista final de features")
    parser.add_argument("--patterns", help="Archivo de patrones prohibidos")
    parser.add_argument("--hook", action="store_true", help="Modo hook: lee JSON por stdin")
    parser.add_argument(
        "--include",
        action="append",
        default=[],
        help="En modo hook, solo escanear rutas que coincidan (glob relativo al proyecto). Repetible.",
    )
    args = parser.parse_args()

    project_dir = Path(os.environ.get("CLAUDE_PROJECT_DIR") or Path.cwd())
    findings: list[str] = []

    if args.hook:
        target, project_dir = hook_target(args.include)
        if target is None:
            return 0
        patterns = load_patterns(find_patterns_file(args.patterns, project_dir))
        findings = scan_code_files([target], patterns)
    else:
        patterns_file = find_patterns_file(args.patterns, project_dir)
        patterns = load_patterns(patterns_file)
        if args.features:
            findings += scan_features(Path(args.features), patterns)
        findings += scan_code_files([Path(f) for f in args.files], patterns)
        if not args.features and not args.files:
            parser.error("indicar --features, archivos de código o --hook")

    if not findings:
        return 0

    header = (
        "Posible leakage: columnas que no estarían disponibles en el punto de decisión.\n"
        "Si el uso es legítimo (por ejemplo, construir el target), agregar el comentario "
        f"'{ALLOW_MARKER}' en esa línea y explicar por qué.\n"
    )
    print(header + "\n".join(findings), file=sys.stderr)
    return 2 if args.hook else 1


if __name__ == "__main__":
    sys.exit(main())
