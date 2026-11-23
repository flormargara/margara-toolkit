#!/usr/bin/env python3
"""PSI / CSI entre una muestra de referencia y una actual.

Uso como librería:
  from psi import psi
  valor, tabla = psi(referencia, actual, bins=10)

Uso por línea de comandos (CSV):
  psi.py referencia.csv actual.csv --column score
  psi.py referencia.csv actual.csv --all-numeric      CSI de cada columna numérica

Los cortes se calculan con cuantiles de la referencia y se aplican a ambas
muestras. Los faltantes van a un bin propio. Bins vacíos usan un piso de
0.0001 para que el logaritmo esté definido.

Lectura: < 0.10 estable; 0.10-0.25 moderado (investigar); > 0.25 significativo.

Solo biblioteca estándar.
"""

from __future__ import annotations

import argparse
import csv
import math
import sys
from bisect import bisect_right

FLOOR = 1e-4


def _to_float(value) -> float | None:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return None if isinstance(value, float) and math.isnan(value) else float(value)
    text = str(value).strip()
    if text == "" or text.lower() in {"na", "nan", "null", "none"}:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def _quantile_edges(values: list[float], bins: int) -> list[float]:
    data = sorted(values)
    edges = []
    for i in range(1, bins):
        pos = i * (len(data) - 1) / bins
        lo, hi = math.floor(pos), math.ceil(pos)
        edges.append(data[lo] + (data[hi] - data[lo]) * (pos - lo))
    return sorted(set(edges))


def _distribution(values, edges) -> list[float]:
    counts = [0] * (len(edges) + 2)  # bins numéricos + bin de faltantes al final
    for v in values:
        f = _to_float(v)
        counts[-1 if f is None else bisect_right(edges, f)] += 1
    total = sum(counts) or 1
    return [c / total for c in counts]


def psi(reference, actual, bins: int = 10):
    """Devuelve (psi, tabla). Tabla: lista de (bin, ref%, act%, contribución)."""
    ref_numeric = [f for f in (_to_float(v) for v in reference) if f is not None]
    if not ref_numeric:
        raise ValueError("la referencia no tiene valores numéricos")
    edges = _quantile_edges(ref_numeric, bins)
    ref_dist = _distribution(reference, edges)
    act_dist = _distribution(actual, edges)

    labels = []
    bounds = [-math.inf] + edges + [math.inf]
    for lo, hi in zip(bounds[:-1], bounds[1:]):
        labels.append(f"({lo:.4g}, {hi:.4g}]")
    labels.append("faltante")

    table, total = [], 0.0
    for label, r, a in zip(labels, ref_dist, act_dist):
        if r == 0 and a == 0:
            continue
        r_, a_ = max(r, FLOOR), max(a, FLOOR)
        contrib = (a_ - r_) * math.log(a_ / r_)
        total += contrib
        table.append((label, r, a, contrib))
    return total, table


def lectura(value: float) -> str:
    if value < 0.10:
        return "estable"
    if value <= 0.25:
        return "moderado: investigar"
    return "significativo: revisar desempeño"


def _read_csv(path: str) -> dict[str, list[str]]:
    with open(path, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        cols: dict[str, list[str]] = {name: [] for name in reader.fieldnames or []}
        for row in reader:
            for name in cols:
                cols[name].append(row.get(name, ""))
    return cols


def _is_numeric(values: list[str]) -> bool:
    present = [v for v in values if _to_float(v) is not None]
    return len(present) >= max(1, 0.5 * len([v for v in values if str(v).strip()]))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("reference")
    parser.add_argument("actual")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--column", help="Columna a comparar (por ejemplo, el score)")
    group.add_argument("--all-numeric", action="store_true", help="CSI de todas las columnas numéricas")
    parser.add_argument("--bins", type=int, default=10)
    parser.add_argument("--fail-above", type=float, help="Salir con código 1 si algún PSI supera este valor")
    args = parser.parse_args()

    ref, act = _read_csv(args.reference), _read_csv(args.actual)
    columns = [args.column] if args.column else [c for c in ref if c in act and _is_numeric(ref[c])]

    worst = 0.0
    for col in columns:
        if col not in ref or col not in act:
            print(f"{col}: no está en ambos archivos", file=sys.stderr)
            return 2
        value, table = psi(ref[col], act[col], bins=args.bins)
        worst = max(worst, value)
        print(f"{col}: PSI = {value:.4f} ({lectura(value)})")
        if args.column:
            print(f"  {'bin':<28}{'ref%':>8}{'act%':>8}{'aporte':>10}")
            for label, r, a, c in table:
                print(f"  {label:<28}{r:>8.2%}{a:>8.2%}{c:>10.4f}")

    if args.fail_above is not None and worst > args.fail_above:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
