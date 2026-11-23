#!/usr/bin/env python3
"""Gate de integridad del dataset de modelado (matriz universo + features).

Entrada: un CSV de la matriz por partición y, opcionalmente, el CSV del universo
de cada partición (el que alimentó la receta).

Uso:
  check_dataset.py --split train=matriz_train.csv --split val=matriz_val.csv \
      --split score=matriz_score.csv --universe train=univ_train.csv \
      --universe val=univ_val.csv --id-col cod_persona --target-cols target

Chequeos:
  1. Sin duplicados de grano: 0 filas repetidas de (entidad, fecha_corte) por partición.
  2. Filas preservadas: filas de la matriz = filas del universo (si se pasa --universe).
  3. Target preservado: suma de cada columna de target = la del universo (si se pasa --universe).
  4. Sin superposición temporal: ninguna fecha de corte de otra partición aparece en train.
  5. Faltantes: ninguna columna completamente vacía en una partición (FAIL); la tasa
     de faltantes de una columna no se aleja de la de train más que --max-null-shift (WARN).
  6. Esquema idéntico: mismas columnas en el mismo orden en todas las particiones
     (las de scoring se comparan sin las columnas de target).

Las particiones cuyo nombre es score, scoring, prediccion o inference no llevan target.

Salida: 0 si todo pasa; 1 si algún chequeo falla. Solo biblioteca estándar.
"""

from __future__ import annotations

import argparse
import csv
import sys
from collections import defaultdict

SCORE_SPLITS = {"score", "scoring", "prediccion", "predicción", "inference"}
NULLS = {"", "na", "nan", "null", "none", "nat"}


def parse_pairs(values: list[str], flag: str) -> dict[str, str]:
    out = {}
    for v in values or []:
        if "=" not in v:
            raise SystemExit(f"{flag} espera particion=archivo, recibió {v!r}")
        name, path = v.split("=", 1)
        out[name.strip().lower()] = path.strip()
    return out


def is_null(value: str | None) -> bool:
    return value is None or value.strip().lower() in NULLS


def to_float(value: str) -> float | None:
    if is_null(value):
        return None
    try:
        return float(value)
    except ValueError:
        return None


def profile(path: str, id_col: str, date_col: str, target_cols: list[str]) -> dict:
    with open(path, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        columns = list(reader.fieldnames or [])
        missing = [c for c in (id_col, date_col) if c not in columns]
        if missing:
            raise SystemExit(f"columnas ausentes en {path}: {', '.join(missing)}")
        seen, dups, rows = set(), 0, 0
        dates = set()
        nulls = defaultdict(int)
        sums = {t: 0.0 for t in target_cols if t in columns}
        bad_target = defaultdict(int)
        for row in reader:
            rows += 1
            key = (row[id_col].strip(), row[date_col].strip())
            dups += key in seen
            seen.add(key)
            dates.add(row[date_col].strip())
            for c in columns:
                if is_null(row.get(c)):
                    nulls[c] += 1
            for t in sums:
                v = to_float(row[t])
                if v is None:
                    bad_target[t] += 1
                else:
                    sums[t] += v
    return {
        "columns": columns, "rows": rows, "dups": dups, "dates": dates,
        "nulls": nulls, "sums": sums, "bad_target": bad_target,
    }


def close(a: float, b: float, tol: float = 1e-6) -> bool:
    return abs(a - b) <= tol * max(1.0, abs(a), abs(b))


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--split", action="append", required=True, help="particion=matriz.csv (repetible)")
    p.add_argument("--universe", action="append", help="particion=universo.csv (repetible)")
    p.add_argument("--id-col", required=True)
    p.add_argument("--date-col", default="fecha_corte")
    p.add_argument("--target-cols", default="target", help="Columnas de target separadas por coma")
    p.add_argument("--train-split", default="train")
    p.add_argument("--max-null-shift", type=float, default=0.20,
                   help="Diferencia absoluta máxima de tasa de faltantes contra train (WARN)")
    args = p.parse_args()

    splits = parse_pairs(args.split, "--split")
    universes = parse_pairs(args.universe, "--universe")
    targets = [t.strip() for t in args.target_cols.split(",") if t.strip()]
    results: list[tuple[str, str]] = []

    prof = {name: profile(path, args.id_col, args.date_col, targets) for name, path in splits.items()}
    uprof = {name: profile(path, args.id_col, args.date_col, targets) for name, path in universes.items()}

    for name, pr in prof.items():
        if pr["rows"] == 0:
            results.append(("FAIL", f"{name}: partición vacía"))

    # 1. Duplicados de grano
    for name, pr in prof.items():
        results.append(("OK" if not pr["dups"] else "FAIL", f"duplicados ({args.id_col}, {args.date_col}) en {name}: {pr['dups']}"))

    # 2 y 3. Filas y target preservados contra el universo
    for name, pr in prof.items():
        if name not in uprof:
            results.append(("MANUAL", f"{name}: sin --universe, no se verifican filas ni target preservados"))
            continue
        up = uprof[name]
        ok = pr["rows"] == up["rows"]
        results.append(("OK" if ok else "FAIL", f"filas {name}: matriz {pr['rows']} vs universo {up['rows']}"))
        if name in SCORE_SPLITS:
            continue
        for t in targets:
            if t not in pr["sums"]:
                results.append(("FAIL", f"target {t} ausente en la matriz de {name}"))
                continue
            if t not in up["sums"]:
                results.append(("WARN", f"target {t} ausente en el universo de {name}; no se compara"))
                continue
            ok = close(pr["sums"][t], up["sums"][t])
            results.append(("OK" if ok else "FAIL",
                            f"suma de {t} en {name}: matriz {pr['sums'][t]:g} vs universo {up['sums'][t]:g}"))

    # Target válido en particiones etiquetadas
    for name, pr in prof.items():
        if name in SCORE_SPLITS:
            continue
        for t in targets:
            if t in pr["sums"] and pr["bad_target"][t]:
                results.append(("FAIL", f"{t} en {name}: {pr['bad_target'][t]} filas vacías o no numéricas"))

    # 4. Superposición temporal con train
    train = prof.get(args.train_split)
    if train is None:
        results.append(("WARN", f"no hay partición {args.train_split!r}; no se evalúa superposición ni faltantes contra train"))
    else:
        for name, pr in prof.items():
            if name == args.train_split:
                continue
            shared = sorted(train["dates"] & pr["dates"])
            results.append(("OK" if not shared else "FAIL",
                            f"fechas de corte de {name} presentes en {args.train_split}: {len(shared)}"
                            + (f" (ej.: {', '.join(shared[:5])})" if shared else "")))

    # 5. Faltantes
    for name, pr in prof.items():
        if not pr["rows"]:
            continue
        empty = [c for c in pr["columns"] if pr["nulls"][c] == pr["rows"]]
        results.append(("OK" if not empty else "FAIL",
                        f"columnas completamente vacías en {name}: {len(empty)}" + (f" ({', '.join(empty[:10])})" if empty else "")))
        if train is not None and name != args.train_split and train["rows"]:
            shifted = []
            for c in pr["columns"]:
                if c in targets or c not in train["columns"]:
                    continue
                a = train["nulls"][c] / train["rows"]
                b = pr["nulls"][c] / pr["rows"]
                if abs(a - b) > args.max_null_shift:
                    shifted.append(f"{c} {a:.0%}→{b:.0%}")
            results.append(("OK" if not shifted else "WARN",
                            f"faltantes que cambian más de {args.max_null_shift:.0%} entre {args.train_split} y {name}: {len(shifted)}"
                            + (f" ({'; '.join(shifted[:10])})" if shifted else "")))

    # 6. Esquema idéntico
    ref_name = args.train_split if args.train_split in prof else next(iter(prof))
    ref = [c for c in prof[ref_name]["columns"] if c not in targets]
    for name, pr in prof.items():
        if name == ref_name:
            continue
        cols = [c for c in pr["columns"] if c not in targets]
        if cols == ref:
            results.append(("OK", f"esquema de {name} igual al de {ref_name}"))
        else:
            missing = [c for c in ref if c not in cols]
            extra = [c for c in cols if c not in ref]
            detail = []
            if missing:
                detail.append(f"faltan {', '.join(missing[:10])}")
            if extra:
                detail.append(f"sobran {', '.join(extra[:10])}")
            if not missing and not extra:
                detail.append("mismas columnas en otro orden")
            results.append(("FAIL", f"esquema de {name} distinto del de {ref_name}: {'; '.join(detail)}"))
        if name not in SCORE_SPLITS:
            absent = [t for t in targets if t not in pr["columns"]]
            if absent:
                results.append(("FAIL", f"{name} no tiene las columnas de target: {', '.join(absent)}"))

    for status, msg in results:
        print(f"{status:<6} {msg}")
    print("MANUAL verificar que train, validación y scoring salen de la misma receta con distinto universo")

    failed = any(s == "FAIL" for s, _ in results)
    print("\nVeredicto:", "❌ el dataset no está listo" if failed else "✅ dataset íntegro")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
