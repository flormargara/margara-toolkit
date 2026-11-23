#!/usr/bin/env python3
"""Chequeo del grupo de control de un modelo de cobranzas.

Entrada: el registro de asignaciones en CSV, una fila por cuenta (o cliente) y corrida,
con el rating y el grupo asignado. Opcionalmente, el target observado, para verificar
que el control alcanza para reentrenar.

Uso:
  check_control_group.py asignaciones.csv --expected A=0.03,B=0.05,C=0.08
  check_control_group.py asignaciones.csv --expected 0.05 --id-col cliente \
      --target-col pase_tramo --min-control-events 100

Chequeos (FAIL hace salir con 1):
  1. Persistencia: una cuenta que cayó en control sigue en control en todas las
     corridas, y una tratada nunca pasa a control.                                FAIL
  2. Proporción por rating: la proporción de unidades en control (contadas una vez,
     con el rating de su primera asignación) no se aleja de la esperada más de
     --sigmas desvíos binomiales.                                                FAIL
  3. Tamaño para reentrenar: filas de control por rating >= --min-control-rows y,
     con --target-col, eventos de control por rating >= --min-control-events.    FAIL
  4. Grupo vacío o fuera de --control-value / --treatment-value.                  FAIL

El control se usa para dos cosas: medir el impacto y reentrenar el modelo. Por eso
el tamaño se revisa por rating y contra los dos objetivos.

Salida: 0 si todo pasa; 1 si algún chequeo falla. Solo biblioteca estándar.
"""

from __future__ import annotations

import argparse
import csv
import math
import sys
from collections import defaultdict
from datetime import date, datetime

NULLS = {"", "na", "nan", "null", "none"}


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
    p.add_argument("assignments")
    p.add_argument("--id-col", default="id", help="Unidad que tiene que persistir en su grupo")
    p.add_argument("--run-col", default="fecha_corrida")
    p.add_argument("--rating-col", default="rating")
    p.add_argument("--group-col", default="grupo")
    p.add_argument("--control-value", default="control")
    p.add_argument("--treatment-value", default="tratamiento")
    p.add_argument("--expected", required=True,
                   help="Proporción de control esperada: un número para todos los ratings o A=0.03,B=0.05")
    p.add_argument("--target-col", help="Target observado (1 = evento), para contar eventos de control")
    p.add_argument("--min-control-rows", type=int, default=0)
    p.add_argument("--min-control-events", type=int, default=0)
    p.add_argument("--sigmas", type=float, default=3.0)
    args = p.parse_args()

    if "=" in args.expected:
        expected = {k.strip(): float(v) for k, v in (x.split("=", 1) for x in args.expected.split(",") if x.strip())}
        default = None
    else:
        expected, default = {}, float(args.expected)

    groups_by_id: dict[str, set[str]] = defaultdict(set)
    first_group: dict[str, tuple[str, str]] = {}
    switches: list[str] = []
    per_rating = defaultdict(lambda: [0, 0, 0])   # rating -> [filas, filas de control, eventos de control]
    units = defaultdict(lambda: [0, 0])            # rating de la primera asignación -> [unidades, en control]
    bad_group = 0
    valid = {args.control_value, args.treatment_value}

    with open(args.assignments, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        needed = [args.id_col, args.run_col, args.rating_col, args.group_col, args.target_col]
        missing = [c for c in needed if c and c not in (reader.fieldnames or [])]
        if missing:
            raise SystemExit(f"columnas ausentes en {args.assignments}: {', '.join(missing)}")
        rows = list(reader)

    rows.sort(key=lambda r: parse_date(r[args.run_col]))
    for row in rows:
        g = row[args.group_col].strip()
        if g not in valid:
            bad_group += 1
            continue
        key = row[args.id_col].strip()
        groups_by_id[key].add(g)
        if key not in first_group:
            first_group[key] = (g, row[args.run_col])
            u = units[row[args.rating_col].strip()]
            u[0] += 1
            u[1] += g == args.control_value
        elif first_group[key][0] != g and len(switches) < 5:
            switches.append(f"{key} ({first_group[key][0]} {first_group[key][1]} → {g} {row[args.run_col]})")
        stats = per_rating[row[args.rating_col].strip()]
        stats[0] += 1
        if g == args.control_value:
            stats[1] += 1
            if args.target_col:
                v = row[args.target_col].strip().lower()
                if v not in NULLS and float(v) >= 1:
                    stats[2] += 1

    results: list[tuple[str, str]] = []
    results.append(("OK" if not bad_group else "FAIL",
                    f"filas con grupo vacío o desconocido: {bad_group}"))

    switched = sum(1 for gs in groups_by_id.values() if len(gs) > 1)
    results.append(("OK" if not switched else "FAIL",
                    f"persistencia: {switched} de {len(groups_by_id)} unidades cambiaron de grupo"
                    + (f" (ej.: {'; '.join(switches)})" if switched else "")))

    print(f"{'rating':<10}{'unidades':>9}{'control':>9}{'prop.':>8}{'esperada':>10}{'±3σ':>8}"
          f"{'filas ctrl':>11}{'eventos':>9}")
    for rating in sorted(set(per_rating) | set(units)):
        _, c_rows, ev = per_rating[rating]
        n, c = units[rating]
        exp = expected.get(rating, default)
        prop = c / n if n else 0
        if exp is None:
            results.append(("FAIL", f"rating {rating} sin proporción esperada en --expected"))
            band = "—"
        else:
            sd = math.sqrt(exp * (1 - exp) / n) if n else 0
            ok = abs(prop - exp) <= args.sigmas * sd
            band = f"{args.sigmas * sd:.2%}"
            results.append(("OK" if ok else "FAIL",
                            f"proporción {rating}: {prop:.2%} vs {exp:.2%} (±{band})"))
        print(f"{rating:<10}{n:>9}{c:>9}{prop:>8.2%}{('—' if exp is None else f'{exp:.2%}'):>10}"
              f"{band:>8}{c_rows:>11}{(ev if args.target_col else '—'):>9}")
        if args.min_control_rows:
            results.append(("OK" if c_rows >= args.min_control_rows else "FAIL",
                            f"tamaño {rating}: {c_rows} filas de control (mínimo {args.min_control_rows})"))
        if args.target_col and args.min_control_events:
            results.append(("OK" if ev >= args.min_control_events else "FAIL",
                            f"eventos {rating}: {ev} en control (mínimo {args.min_control_events} para reentrenar)"))
    print()

    for status, msg in results:
        print(f"{status:<5} {msg}")
    print("MANUAL documentar qué recibe el control (mínimos regulatorios) y sus exclusiones con volumen")
    if not (args.min_control_rows or args.min_control_events):
        print("MANUAL fijar --min-control-rows o --min-control-events: el control también alimenta el reentrenamiento")

    failed = any(s == "FAIL" for s, _ in results)
    print("\nVeredicto:", "❌ el grupo de control no cumple" if failed else "✅ grupo de control verificado")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
