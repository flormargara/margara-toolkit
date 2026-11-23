#!/usr/bin/env python3
"""Compone el catálogo de golden rules de ai-mllc a partir de los dominios del toolkit.

ai-mllc lee un único `mllc-golden-rules.md` en la carpeta de configuración del
proyecto (`.cursor/`, `.kiro/` o `.github/`). Este script junta los catálogos de
`adapters/mllc/golden-rules/<dominio>.md`, valida el formato que exige el núcleo de
ai-mllc y escribe el resultado.

Uso:
  compose.py --check                                   # solo valida los catálogos
  compose.py ml-foundations --out -                    # imprime el catálogo
  compose.py ml-foundations --out .cursor/mllc-golden-rules.md
  compose.py ml-foundations --out .cursor/mllc-golden-rules.md --force

Formato validado (el mismo que rechaza el núcleo): cada `## ` fuera de un bloque de
código abre una regla `## <id> (v<n>)`; abajo, la lista con fuerza, etapa, mecanismo y
estado, y después el enunciado en prosa. Un id y versión no se repiten entre dominios.

ai-mllc trata el catálogo como dato del proyecto y nunca lo pisa; este script tampoco,
salvo con --force.

Salida: 0 si todo es válido y se escribió; 1 ante un problema. Solo biblioteca estándar.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CATALOGS = HERE / "golden-rules"

STAGES = ("intake", "understand", "observe", "features", "dataset", "model", "deploy")
ALLOWED = {
    "fuerza": {"bloqueante", "alerta", "sugerencia"},
    "etapa": set(STAGES),
    "mecanismo": {"check_determinista", "atestacion", "discusion"},
    "estado": {"draft", "active"},
}
HEADING = re.compile(r"^##(?!#)\s*(.*?)\s*$")
HEADER = re.compile(r"^(\S+)\s+\(v(\d+)\)$")
META = re.compile(r"^[-*]\s+([^:]+?)\s*:\s*(.*?)\s*$")


def sections(text: str) -> tuple[list[str], list[tuple[str, list[str]]]]:
    """Devuelve el preámbulo y las secciones (encabezado, cuerpo), ignorando bloques de código."""
    preamble: list[str] = []
    out: list[tuple[str, list[str]]] = []
    in_fence = False
    for line in text.splitlines():
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
        m = None if in_fence else HEADING.match(line)
        if m:
            out.append((m.group(1), []))
        elif out:
            out[-1][1].append(line)
        else:
            preamble.append(line)
    return preamble, out


def validate(name: str, text: str) -> tuple[list[tuple[str, int, dict]], list[str]]:
    _, secs = sections(text)
    rules, problems = [], []
    for heading, body in secs:
        hm = HEADER.match(heading)
        if not hm or int(hm.group(2)) < 1:
            problems.append(f"{name}: encabezado inválido {heading!r} (se espera '<id> (v<n>)')")
            continue
        rid, ver = hm.group(1), int(hm.group(2))
        meta, i = {}, 0
        while i < len(body):
            line = body[i].strip()
            if not line:
                i += 1
                continue
            mm = META.match(line)
            if not mm:
                break
            key = mm.group(1).lower()
            if key not in ALLOWED:
                problems.append(f"{name}: {rid}: clave desconocida {key!r}")
            elif key in meta:
                problems.append(f"{name}: {rid}: clave repetida {key!r}")
            meta[key] = mm.group(2)
            i += 1
        for key, values in ALLOWED.items():
            if key not in meta:
                problems.append(f"{name}: {rid}: falta {key}")
            elif meta[key] not in values:
                problems.append(f"{name}: {rid}: {key} {meta[key]!r} no es uno de {', '.join(sorted(values))}")
        if not "\n".join(body[i:]).strip():
            problems.append(f"{name}: {rid}: sin enunciado")
        rules.append((rid, ver, meta))
    if not secs:
        problems.append(f"{name}: no tiene reglas")
    return rules, problems


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("domains", nargs="*", help="Dominios a incluir, en orden (por ejemplo ml-foundations)")
    p.add_argument("--out", help="Archivo de salida, o '-' para la salida estándar")
    p.add_argument("--force", action="store_true", help="Sobrescribir --out si ya existe")
    p.add_argument("--check", action="store_true", help="Validar todos los catálogos y no escribir nada")
    args = p.parse_args()

    available = {f.stem: f for f in sorted(CATALOGS.glob("*.md"))}
    domains = list(available) if args.check else args.domains
    if not domains:
        p.error(f"indicar al menos un dominio; disponibles: {', '.join(available)}")
    unknown = [d for d in domains if d not in available]
    if unknown:
        print(f"dominios sin catálogo: {', '.join(unknown)}; disponibles: {', '.join(available)}", file=sys.stderr)
        return 1

    problems, seen, bodies, total = [], {}, [], 0
    for d in domains:
        text = available[d].read_text(encoding="utf-8")
        rules, probs = validate(d, text)
        problems += probs
        for rid, ver, _ in rules:
            if (rid, ver) in seen:
                problems.append(f"{d}: {rid} (v{ver}) ya está definida en {seen[(rid, ver)]}")
            seen[(rid, ver)] = d
        total += len(rules)
        _, secs = sections(text)
        bodies.append((d, secs))

    if problems:
        for msg in problems:
            print(f"FAIL {msg}", file=sys.stderr)
        return 1
    print(f"OK {total} reglas válidas en {', '.join(domains)}", file=sys.stderr)
    if args.check:
        return 0
    if not args.out:
        p.error("falta --out (o usar --check)")

    lines = [
        "# MLLC golden rules — este proyecto",
        "",
        f"Generado desde margara-toolkit (adapters/mllc) con los dominios: {', '.join(domains)}.",
        "Para adaptar una regla a este proyecto, editarla acá; para cambiar su sentido, agregar una versión nueva.",
        "Volver a generarlo pisa las ediciones locales.",
        "",
    ]
    for _, secs in bodies:
        for heading, body in secs:
            lines.append(f"## {heading}")
            lines.extend(body)
            if lines[-1].strip():
                lines.append("")
    text = "\n".join(lines).rstrip() + "\n"

    if args.out == "-":
        sys.stdout.write(text)
        return 0
    out = Path(args.out)
    if out.exists() and not args.force:
        print(f"{out} ya existe; ai-mllc lo trata como dato del proyecto. Usar --force para pisarlo.", file=sys.stderr)
        return 1
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding="utf-8")
    print(f"escrito {out}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
