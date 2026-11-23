#!/usr/bin/env python3
"""Verifica que un modelo de cobranzas se entrene y evalúe solo con el grupo de control.

Una vez que el modelo decide a quién se gestiona, el resultado de las cuentas
tratadas refleja la gestión y no el riesgo original. Entrenar o evaluar con ellas
hace que el modelo aprenda de su propio efecto.

Entrada: el universo o el dataset de entrenamiento en CSV, con la fecha de corte
(entrada al tramo) y el grupo de cada fila.

Uso:
  check_training_population.py universo.csv --model-start 2026-03-01
  check_training_population.py universo.csv --model-start 2026-03-01 --target-kind autocura \
      --untreated-values control,sin_gestion --split-col split

Chequeos (FAIL hace salir con 1):
  1. Desde --model-start (primer día de gestión guiada por el modelo), toda fila es
     de control.                                                                  FAIL
  2. Desde --model-start, ninguna fila con grupo vacío.                           FAIL
  3. Con --target-kind autocura, toda fila, de cualquier fecha, es de control o sin
     gestión (--untreated-values): en las gestionadas no se puede separar la
     autocura del efecto de la gestión.                                           FAIL
Las filas anteriores a --model-start se aceptan para pase de tramo y se informan:
documentar qué gestión recibieron. Las filas de scoring (--split-col) no se evalúan.

Salida: 0 si todo pasa; 1 si algún chequeo falla. Solo biblioteca estándar.
"""

from __future__ import annotations

import argparse
import csv
import sys
from collections import Counter, defaultdict
from datetime import date, datetime

NULLS = {"", "na", "nan", "null", "none"}
SCORE_SPLITS = {"score", "scoring", "prediccion", "predicción", "inference"}


def parse_date(text: str) -> date:
    text = text.strip()
    for fmt in ("%Y-%m-%d", "%Y-%m-%d %H:%M:%S", "%Y%m%d", "%Y-%m", "%Y%m", "%d/%m/%Y"):
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            continue
    raise SystemExit(f"fecha no reconocida: {text!r}")


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("data")
    p.add_argument("--model-start", required=True, help="Primer día de gestión guiada por el modelo")
    p.add_argument("--date-col", default="fecha_corte")
    p.add_argument("--group-col", default="grupo")
    p.add_argument("--control-value", default="control")
    p.add_argument("--target-kind", choices=["pase", "autocura"], default="pase")
    p.add_argument("--untreated-values", default="control,sin_gestion",
                   help="Grupos sin gestión válidos para autocura")
    p.add_argument("--split-col", help="Partición; las filas de scoring no se evalúan")
    args = p.parse_args()

    start = parse_date(args.model_start)
    untreated = {x.strip() for x in args.untreated_values.split(",") if x.strip()} | {args.control_value}

    by_split = defaultdict(Counter)   # split -> Counter de estados
    examples: dict[str, list[str]] = defaultdict(list)
    pre_groups = Counter()

    with open(args.data, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        needed = [args.date_col, args.group_col, args.split_col]
        missing = [c for c in needed if c and c not in (reader.fieldnames or [])]
        if missing:
            raise SystemExit(f"columnas ausentes en {args.data}: {', '.join(missing)}")
        for i, row in enumerate(reader, start=2):
            split = row[args.split_col].strip().lower() if args.split_col else "todo"
            if split in SCORE_SPLITS:
                continue
            d = parse_date(row[args.date_col])
            g = row[args.group_col].strip()
            empty = g.lower() in NULLS
            c = by_split[split]
            c["filas"] += 1
            if d >= start:
                c["post"] += 1
                if empty:
                    c["post_vacio"] += 1
                    if len(examples["vacío"]) < 3:
                        examples["vacío"].append(f"línea {i}")
                elif g != args.control_value:
                    c["post_tratado"] += 1
                    if len(examples["tratado"]) < 3:
                        examples["tratado"].append(f"línea {i} ({g}, {d})")
            else:
                c["pre"] += 1
                pre_groups[g or "(vacío)"] += 1
            if args.target_kind == "autocura" and (empty or g not in untreated):
                c["autocura_gestionado"] += 1
                if len(examples["autocura"]) < 3:
                    examples["autocura"].append(f"línea {i} ({g or 'vacío'}, {d})")

    if not by_split:
        print("no hay filas para evaluar", file=sys.stderr)
        return 1

    print(f"Inicio de la gestión guiada por el modelo: {start}\n")
    print(f"{'partición':<12}{'filas':>9}{'antes':>9}{'desde':>9}{'tratadas':>10}{'vacías':>9}")
    for split, c in sorted(by_split.items()):
        print(f"{split:<12}{c['filas']:>9}{c['pre']:>9}{c['post']:>9}{c['post_tratado']:>10}{c['post_vacio']:>9}")
    print()

    results: list[tuple[str, str]] = []
    for split, c in sorted(by_split.items()):
        results.append(("OK" if not c["post_tratado"] else "FAIL",
                        f"{split}: {c['post_tratado']} filas tratadas desde {start}"
                        + (f" (ej.: {'; '.join(examples['tratado'])})" if c["post_tratado"] else "")))
        if c["post_vacio"]:
            results.append(("FAIL", f"{split}: {c['post_vacio']} filas sin grupo desde {start} "
                                    f"(ej.: {'; '.join(examples['vacío'])})"))
        if args.target_kind == "autocura":
            n = c["autocura_gestionado"]
            results.append(("OK" if not n else "FAIL",
                            f"{split}: {n} filas gestionadas en un target de autocura"
                            + (f" (ej.: {'; '.join(examples['autocura'])})" if n else "")))

    for status, msg in results:
        print(f"{status:<5} {msg}")
    pre = sum(c["pre"] for c in by_split.values())
    if pre and args.target_kind == "pase":
        detail = ", ".join(f"{g}: {n}" for g, n in pre_groups.most_common())
        print(f"MANUAL {pre} filas anteriores al modelo ({detail}): documentar qué gestión recibieron")

    failed = any(s == "FAIL" for s, _ in results)
    print("\nVeredicto:", "❌ hay filas afectadas por la gestión" if failed
          else "✅ entrenamiento y evaluación solo con población sin gestión guiada")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
