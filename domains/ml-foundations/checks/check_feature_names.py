#!/usr/bin/env python3
"""Valida los nombres de features contra el estándar y devuelve el tipo de cada una.

Formato: <FUENTE>_<DOMINIO>_<OPERACION>_<DESCRIPCION>_<VENTANA>, en mayúsculas
(ver knowledge/03-features.md, "Nombres"). El tipo se deduce del segmento de
operación, nunca de un substring del nombre: FLG → bandera, CAT → categórica,
el resto del catálogo → numérica.

Usos:
  check_feature_names.py features.txt                una feature por línea
  check_feature_names.py dataset.csv --ignore id,fecha_corte,target
                                                     toma los nombres del encabezado
  check_feature_names.py features.txt --sources BUR,APP --domains TAR,PRE
                                                     además exige fuentes y dominios válidos
  check_feature_names.py features.txt --extra-ops RSI,PER --types-out tipos.csv

Salida: 0 si todos los nombres cumplen; 1 si alguno no cumple o se repite.
Solo usa la biblioteca estándar.
"""

from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path

FLAG_OPS = {"FLG"}
CATEGORICAL_OPS = {"CAT"}
NUMERIC_OPS = {
    "CNT", "SUM", "MTO", "AVG", "MED", "MOD", "STD", "VAR", "MAX", "MIN", "PCT",
    "RAT", "DIF", "TEN", "TDC", "RCD", "RCM", "IDX", "ZSCORE",
}

CODE = re.compile(r"^[A-Z][A-Z0-9]{1,5}$")
DESCRIPTION = re.compile(r"^[A-Z0-9]+$")
WINDOW = re.compile(r"^([1-9][0-9]*[HDM]|NO)$")


def read_names(path: Path, ignore: set[str]) -> list[tuple[int, str]]:
    """(línea o columna, nombre). Un .csv aporta su encabezado; otro archivo, una por línea."""
    if path.suffix.lower() == ".csv":
        with open(path, newline="", encoding="utf-8") as fh:
            header = next(csv.reader(fh), [])
        names = [(i, n.strip()) for i, n in enumerate(header, start=1)]
    else:
        names = [
            (i, line.strip())
            for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1)
        ]
    return [(i, n) for i, n in names if n and not n.startswith("#") and n not in ignore]


def feature_type(operation: str) -> str:
    if operation in FLAG_OPS:
        return "bandera"
    if operation in CATEGORICAL_OPS:
        return "categórica"
    return "numérica"


def problems_for(name: str, operations: set[str], sources: set[str], domains: set[str]) -> list[str]:
    if name != name.upper():
        return ["no está en mayúsculas"]
    if "-" in name:
        return ["tiene '-'"]
    parts = name.split("_")
    if len(parts) != 5:
        return [f"tiene {len(parts)} segmentos; se esperan 5 (FUENTE_DOMINIO_OPERACION_DESCRIPCION_VENTANA)"]
    source, domain, operation, description, window = parts
    out = []
    if not CODE.match(source):
        out.append(f"fuente '{source}' no es un código corto (2 a 6 letras o dígitos, empieza con letra)")
    elif sources and source not in sources:
        out.append(f"fuente '{source}' no está en la lista del proyecto")
    if not CODE.match(domain):
        out.append(f"dominio '{domain}' no es un código corto (2 a 6 letras o dígitos, empieza con letra)")
    elif domains and domain not in domains:
        out.append(f"dominio '{domain}' no está en la lista del proyecto")
    if operation not in operations:
        out.append(f"operación '{operation}' no está en el catálogo")
    if not DESCRIPTION.match(description):
        out.append(f"descripción '{description}' tiene caracteres fuera de A-Z y 0-9")
    if window == "HIST":
        out.append("'HIST' no es una ventana: va en la descripción y la ventana es NO")
    elif not WINDOW.match(window):
        out.append(f"ventana '{window}' no es <n>H, <n>D, <n>M ni NO")
    return out


def split_list(value: str | None) -> set[str]:
    return {v.strip().upper() for v in (value or "").split(",") if v.strip()}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("path", help="Lista de features (una por línea) o CSV con los nombres en el encabezado")
    parser.add_argument("--ignore", help="Columnas que no son features (claves, fecha de corte, target), separadas por coma")
    parser.add_argument("--sources", help="Fuentes válidas del proyecto, separadas por coma")
    parser.add_argument("--domains", help="Dominios válidos del proyecto, separados por coma")
    parser.add_argument("--extra-ops", help="Operaciones numéricas que el proyecto suma al catálogo")
    parser.add_argument("--types-out", help="CSV de salida con nombre y tipo inferido de cada feature válida")
    args = parser.parse_args()

    ignore = {v.strip() for v in (args.ignore or "").split(",") if v.strip()}
    operations = FLAG_OPS | CATEGORICAL_OPS | NUMERIC_OPS | split_list(args.extra_ops)
    sources, domains = split_list(args.sources), split_list(args.domains)

    names = read_names(Path(args.path), ignore)
    if not names:
        print(f"FAIL {args.path}: no hay nombres de features", file=sys.stderr)
        return 1

    failures: list[str] = []
    types: list[tuple[str, str]] = []
    seen: dict[str, int] = {}
    unit = "columna" if Path(args.path).suffix.lower() == ".csv" else "línea"
    for pos, name in names:
        if name in seen:
            failures.append(f"{unit} {pos}: '{name}' repetido (ya en {unit} {seen[name]})")
            continue
        seen[name] = pos
        probs = problems_for(name, operations, sources, domains)
        if probs:
            failures.append(f"{unit} {pos}: '{name}': " + "; ".join(probs))
        else:
            types.append((name, feature_type(name.split("_")[2])))

    counts = {t: sum(1 for _, x in types if x == t) for t in ("numérica", "categórica", "bandera")}
    print(
        f"{len(names)} nombres: {len(types)} válidos "
        f"({counts['numérica']} numéricas, {counts['categórica']} categóricas, {counts['bandera']} banderas), "
        f"{len(failures)} con problemas"
    )
    if args.types_out:
        with open(args.types_out, "w", newline="", encoding="utf-8") as fh:
            writer = csv.writer(fh)
            writer.writerow(["feature", "tipo"])
            writer.writerows(types)
    if failures:
        print("\n".join(f"FAIL {f}" for f in failures), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
