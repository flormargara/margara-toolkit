#!/usr/bin/env python3
"""Chequeos de integridad temporal de un universo de modelado.

Entrada: un CSV con una fila por entidad y snapshot, con al menos la columna de
fecha de corte y la de partición (train / test / val / score). Opcionalmente,
el identificador de la entidad y una columna de fold para backtesting.

Uso:
  check_universe.py universo.csv --horizon-days 90 --last-data-date 2026-10-31
  check_universe.py universo.csv --horizon-days 30 --last-data-date 2026-10-31 \
      --order train,test,val --id-col cod_persona --fold-col fold

Chequeos automáticos:
  1. Orden temporal: max(fecha_corte) de cada partición < min de la siguiente.
  2. Sin solapamiento de horizonte: max(corte anterior) + horizonte <= min(corte siguiente).
  3. Horizonte completo: ninguna fila con target tiene corte + horizonte > último dato.
  4. Entidades repetidas entre particiones (si se indica --id-col).
  5. Duplicados de (entidad, fecha_corte) (si se indica --id-col).
Con --fold-col, 1, 2 y 4 se evalúan dentro de cada fold.
Con --arbiter-overlap, las entidades compartidas con la última partición de --order
(la validación final) son advertencia y no falla: esa partición se reporta completa y
sin entidades vistas. Entre train y test sigue fallando.

No automatizable (se recuerda en la salida): que el filtro de elegibilidad sea
idéntico en train, validación y scoring.

Salida: 0 si todo pasa; 1 si algún chequeo falla. Solo biblioteca estándar.
"""

from __future__ import annotations

import argparse
import csv
import sys
from collections import defaultdict
from datetime import date, datetime, timedelta

SCORE_SPLITS = {"score", "scoring", "prediccion", "predicción", "inference"}


def parse_date(text: str) -> date:
    text = text.strip()
    for fmt in ("%Y-%m-%d", "%Y-%m-%d %H:%M:%S", "%Y%m%d", "%Y-%m", "%Y%m", "%d/%m/%Y"):
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            continue
    raise ValueError(f"fecha no reconocida: {text!r}")


def load(path, date_col, split_col, id_col, fold_col):
    rows = []
    with open(path, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        missing = [c for c in (date_col, split_col, id_col, fold_col) if c and c not in (reader.fieldnames or [])]
        if missing:
            raise SystemExit(f"columnas ausentes en {path}: {', '.join(missing)}")
        for row in reader:
            rows.append(
                {
                    "date": parse_date(row[date_col]),
                    "split": row[split_col].strip().lower(),
                    "id": row[id_col].strip() if id_col else None,
                    "fold": row[fold_col].strip() if fold_col else "_",
                }
            )
    return rows


def check_group(rows, order, horizon, id_col, label, results):
    by_split = defaultdict(list)
    ids = defaultdict(set)
    for r in rows:
        by_split[r["split"]].append(r["date"])
        if id_col:
            ids[r["split"]].add(r["id"])

    present = [s for s in order if s in by_split]
    unknown = sorted(set(by_split) - set(order) - SCORE_SPLITS)
    if unknown:
        results.append(("WARN", label, f"particiones fuera de --order, no evaluadas: {', '.join(unknown)}"))

    for prev, nxt in zip(present, present[1:]):
        prev_max, next_min = max(by_split[prev]), min(by_split[nxt])
        ok = prev_max < next_min
        results.append((
            "OK" if ok else "FAIL", label,
            f"orden temporal {prev} → {nxt}: max {prev} = {prev_max}, min {nxt} = {next_min}",
        ))
        limit = prev_max + timedelta(days=horizon)
        ok = limit <= next_min
        results.append((
            "OK" if ok else "FAIL", label,
            f"horizonte {prev} → {nxt}: {prev_max} + {horizon} d = {limit} {'<=' if ok else '>'} {next_min}",
        ))

    if id_col:
        splits = [s for s in by_split if s not in SCORE_SPLITS]
        for i, a in enumerate(splits):
            for b in splits[i + 1:]:
                shared = ids[a] & ids[b]
                results.append((
                    "OK" if not shared else "FAIL", label,
                    f"entidades compartidas {a} / {b}: {len(shared)}"
                    + (f" (ej.: {', '.join(sorted(shared)[:5])})" if shared else ""),
                ))


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("universe")
    p.add_argument("--horizon-days", type=int, required=True, help="Horizonte del target en días")
    p.add_argument("--last-data-date", required=True, help="Último día con datos de desempeño completos")
    p.add_argument("--date-col", default="fecha_corte")
    p.add_argument("--split-col", default="split")
    p.add_argument("--order", default="train,test,val", help="Particiones en orden temporal esperado")
    p.add_argument("--id-col", help="Identificador de la entidad (persona, cuenta)")
    p.add_argument("--fold-col", help="Columna de fold para backtesting")
    p.add_argument("--allow-entity-overlap", action="store_true",
                   help="No fallar si una entidad aparece en dos particiones (solo con justificación)")
    p.add_argument("--arbiter-overlap", action="store_true",
                   help="Permitir entidades vistas solo en la última partición de --order (la validación "
                        "final, que se reporta completa y sin entidades vistas); entre las demás sigue fallando")
    args = p.parse_args()

    order = [s.strip().lower() for s in args.order.split(",") if s.strip()]
    last = parse_date(args.last_data_date)
    rows = load(args.universe, args.date_col, args.split_col, args.id_col, args.fold_col)
    if not rows:
        print("universo vacío", file=sys.stderr)
        return 1

    results: list[tuple[str, str, str]] = []

    by_fold = defaultdict(list)
    for r in rows:
        by_fold[r["fold"]].append(r)
    for fold, fold_rows in sorted(by_fold.items()):
        label = "" if fold == "_" else f"[fold {fold}] "
        check_group(fold_rows, order, args.horizon_days, args.id_col, label, results)

    labeled = [r for r in rows if r["split"] not in SCORE_SPLITS]
    immature = [r for r in labeled if r["date"] + timedelta(days=args.horizon_days) > last]
    latest_ok = last - timedelta(days=args.horizon_days)
    results.append((
        "OK" if not immature else "FAIL", "",
        f"horizonte completo: {len(immature)} filas con corte posterior a {latest_ok} "
        f"(último dato {last} − {args.horizon_days} d)",
    ))

    if args.id_col:
        seen, dups = set(), 0
        for r in rows:
            key = (r["fold"], r["split"], r["id"], r["date"])
            dups += key in seen
            seen.add(key)
        results.append(("OK" if not dups else "FAIL", "", f"duplicados (entidad, fecha_corte): {dups}"))

    if args.allow_entity_overlap:
        results = [("WARN" if s == "FAIL" and "entidades compartidas" in m else s, l, m) for s, l, m in results]
    elif args.arbiter_overlap and order:
        arbiter = order[-1]
        results = [
            ("WARN" if s == "FAIL" and "entidades compartidas" in m
             and (f"compartidas {arbiter} /" in m or f"/ {arbiter}:" in m) else s, l, m)
            for s, l, m in results
        ]
        results.append(("MANUAL", "", f"reportar {arbiter} en dos vistas: completa y sin entidades vistas en train o test"))

    for status, label, msg in results:
        print(f"{status:<5} {label}{msg}")
    print("MANUAL verificar que el filtro de elegibilidad sea idéntico en train, validación y scoring")

    failed = any(s == "FAIL" for s, _, _ in results)
    print("\nVeredicto:", "❌ no está listo" if failed else "✅ integridad temporal verificada")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
