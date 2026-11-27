#!/usr/bin/env python3
"""Lint del catálogo de skills y de las referencias entre archivos del toolkit.

Chequeos:
  1. Cada carpeta de adapters/claude/skills/ tiene SKILL.md con frontmatter, `name`
     igual al nombre de la carpeta y `description` no vacía.                    FAIL
  2. Los enlaces simbólicos dentro de cada skill apuntan a algo que existe.       FAIL
  3. Ningún SKILL.md ni archivo de domains/ o shared/ tiene rutas absolutas de
     una máquina (/Users/..., /home/..., C:\\...).                                FAIL
  4. Las rutas a archivos .md, .py o .txt escritas entre backticks en SKILL.md,
     domains/ y shared/ existen. Se resuelven igual que las leería un agente:
     relativas al archivo, a la carpeta de su dominio, a domains/ o a la raíz.   FAIL

Un nombre sin carpeta (`check_universe.py`, `04-modelado.md`) vale si existe un archivo
con ese nombre en algún lugar de domains/ o shared/: así se nombran los chequeos.
Se ignoran las rutas con marcadores (<...>, [...], *) y los archivos que crea cada
proyecto: nombres en mayúsculas (AGENTS.md, MODELING_SPEC.md) y los de PROJECT_FILES.

Uso:
  scripts/lint_skills.py
  scripts/lint_skills.py --root <otro checkout del toolkit>

Salida: 0 si todo pasa; 1 si algún chequeo falla. Solo biblioteca estándar.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ABSOLUTE = re.compile(r"(?<![\w.~])(/Users/|/home/|[A-Z]:\\\\)")
PROJECT_FILES = {"forbidden_columns.txt"}
REF = re.compile(r"`([^`\s]+\.(?:md|py|txt))(?::\d+)?`")


def frontmatter(text: str) -> dict[str, str] | None:
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---", 4)
    if end < 0:
        return None
    fields = {}
    for line in text[4:end].splitlines():
        key, sep, value = line.partition(":")
        if sep and not line.startswith((" ", "\t")):
            fields[key.strip()] = value.strip()
    return fields


def ignorable(ref: str) -> bool:
    name = Path(ref).name
    stem = name.rsplit(".", 1)[0]
    return (any(c in ref for c in "<>[]*{}") or name in PROJECT_FILES
            or stem.isupper() or stem.replace("_", "").isupper())


def candidates(ref: str, file: Path, root: Path) -> list[Path]:
    domains = root / "domains"
    out = [file.parent / ref, file.parent.parent / ref, domains / ref, root / ref,
           root / "shared" / "knowledge" / ref.removeprefix("shared/")]
    for parent in file.parents:  # carpeta del dominio (domains/<dominio>/) y de la skill
        if parent.parent == domains or parent.parent.name == "skills":
            out.append(parent / ref)
    return out


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--root", default=str(Path(__file__).resolve().parent.parent))
    args = p.parse_args()
    root = Path(args.root).resolve()
    catalog = root / "adapters" / "claude" / "skills"

    errors: list[str] = []
    skills = sorted(d for d in catalog.iterdir() if d.is_dir()) if catalog.is_dir() else []
    for skill in skills:
        md = skill / "SKILL.md"
        if not md.is_file():
            errors.append(f"{skill.relative_to(root)}: falta SKILL.md")
            continue
        fm = frontmatter(md.read_text(encoding="utf-8"))
        if fm is None:
            errors.append(f"{md.relative_to(root)}: falta el frontmatter")
        else:
            if fm.get("name") != skill.name:
                errors.append(f"{md.relative_to(root)}: name {fm.get('name')!r} no coincide con la carpeta {skill.name!r}")
            if not fm.get("description"):
                errors.append(f"{md.relative_to(root)}: description vacía")
        for link in skill.iterdir():
            if link.is_symlink() and not link.exists():
                errors.append(f"{link.relative_to(root)}: enlace roto -> {link.readlink()}")

    files = [s / "SKILL.md" for s in skills if (s / "SKILL.md").is_file()]
    for base in ("domains", "shared"):
        files += sorted(f for f in (root / base).rglob("*") if f.suffix in {".md", ".py", ".txt"} and f.is_file())

    known = {f.name for base in ("domains", "shared") for f in (root / base).rglob("*") if f.is_file()}
    refs = 0
    for f in files:
        rel = f.relative_to(root)
        text = f.read_text(encoding="utf-8")
        for n, line in enumerate(text.splitlines(), 1):
            if ABSOLUTE.search(line):
                errors.append(f"{rel}:{n}: ruta absoluta")
        if f.suffix != ".md":
            continue
        for n, line in enumerate(text.splitlines(), 1):
            for ref in REF.findall(line):
                if ignorable(ref):
                    continue
                refs += 1
                if "/" not in ref and ref in known:
                    continue
                if not any(c.exists() for c in candidates(ref, f, root)):
                    errors.append(f"{rel}:{n}: no existe {ref}")

    print(f"skills: {len(skills)} · archivos revisados: {len(files)} · referencias: {refs}")
    for e in errors:
        print(f"FAIL  {e}")
    if not errors:
        print("OK    catálogo y referencias en orden")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
