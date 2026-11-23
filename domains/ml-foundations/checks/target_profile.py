#!/usr/bin/env python3
"""Perfil del target por período, antes de definir cortes y particiones.

Entrada, uno de dos modos:
  - Por fila: CSV con una columna de fecha de corte y una de target (binario o numérico).
  - Agregado: CSV con una fila por período, con volumen y suma del target (eventos).

Uso:
  target_profile.py universo.csv --date-col fecha_corte --target-col target
  target_profile.py mensual.csv --agg --period-col periodo --volume-col n --sum-col eventos
  target_profile.py universo.csv --min-events 50 --max-jump 0.4

Reporta por período (mes por defecto): volumen, suma del target y tasa o media; los
mismos agregados por trimestre; coeficiente de variación de la tasa, tendencia anual
relativa y saltos entre períodos consecutivos.

Veredicto:
  viable      todos los períodos con eventos suficientes y sin saltos mayores a --max-jump
  parcial     algunos períodos sin eventos suficientes o con saltos: decir qué rango es viable
  descartado  la mitad o más de los períodos sin eventos suficientes

Salida: 0 si es viable; 1 si es parcial o descartado. Solo biblioteca estándar.
"""

from __future__ import annotations

import argparse
import csv
import statistics
import sys
from collections import defaultdict
from datetime import datetime

NULLS = {"", "na", "nan", "null", "none"}


def period_key(text: str, granularity: str) -> str:
    text = text.strip()
    for fmt in ("%Y-%m-%d", "%Y-%m-%d %H:%M:%S", "%Y%m%d", "%Y-%m", "%Y%m", "%d/%m/%Y"):
        try:
            d = datetime.strptime(text, fmt).date()
            break
        except ValueError:
            continue
    else:
        raise SystemExit(f"fecha no reconocida: {text!r}")
    if granularity == "day":
        return d.isoformat()
    if granularity == "quarter":
        return f"{d.year}-T{(d.month - 1) // 3 + 1}"
    return f"{d.year}-{d.month:02d}"


def quarter_of(month_key: str) -> str:
    y, m = month_key.split("-")[:2]
    if m.startswith("T"):
        return month_key
    return f"{y}-T{(int(m) - 1) // 3 + 1}"


def load_rows(path, date_col, target_col, granularity):
    agg = defaultdict(lambda: [0, 0.0])
    skipped = 0
    with open(path, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        missing = [c for c in (date_col, target_col) if c not in (reader.fieldnames or [])]
        if missing:
            raise SystemExit(f"columnas ausentes en {path}: {', '.join(missing)}")
        for row in reader:
            raw = row[target_col]
            if raw is None or raw.strip().lower() in NULLS:
                skipped += 1
                continue
            try:
                value = float(raw)
            except ValueError:
                skipped += 1
                continue
            key = period_key(row[date_col], granularity)
            agg[key][0] += 1
            agg[key][1] += value
    return agg, skipped


def load_agg(path, period_col, volume_col, sum_col):
    agg = defaultdict(lambda: [0, 0.0])
    with open(path, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        missing = [c for c in (period_col, volume_col, sum_col) if c not in (reader.fieldnames or [])]
        if missing:
            raise SystemExit(f"columnas ausentes en {path}: {', '.join(missing)}")
        for row in reader:
            key = period_key(row[period_col], "month")
            agg[key][0] += int(float(row[volume_col]))
            agg[key][1] += float(row[sum_col])
    return agg, 0


def slope(ys: list[float]) -> float:
    n = len(ys)
    if n < 2:
        return 0.0
    xs = range(n)
    mx, my = (n - 1) / 2, statistics.fmean(ys)
    den = sum((x - mx) ** 2 for x in xs)
    return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / den if den else 0.0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("data")
    p.add_argument("--date-col", default="fecha_corte")
    p.add_argument("--target-col", default="target")
    p.add_argument("--granularity", choices=["day", "month", "quarter"], default="month")
    p.add_argument("--agg", action="store_true", help="La entrada ya está agregada por período")
    p.add_argument("--period-col", default="periodo")
    p.add_argument("--volume-col", default="volumen")
    p.add_argument("--sum-col", default="positivos")
    p.add_argument("--min-events", type=float, default=30,
                   help="Suma mínima del target por período (eventos, en un target binario)")
    p.add_argument("--min-volume", type=int, default=100, help="Volumen mínimo por período")
    p.add_argument("--max-jump", type=float, default=0.5,
                   help="Cambio relativo máximo de la tasa entre períodos consecutivos")
    args = p.parse_args()

    if args.agg:
        agg, skipped = load_agg(args.data, args.period_col, args.volume_col, args.sum_col)
        periods_per_year = 12
    else:
        agg, skipped = load_rows(args.data, args.date_col, args.target_col, args.granularity)
        periods_per_year = {"day": 365, "month": 12, "quarter": 4}[args.granularity]
    if not agg:
        print("sin datos", file=sys.stderr)
        return 1

    keys = sorted(agg)
    rates = [agg[k][1] / agg[k][0] if agg[k][0] else 0.0 for k in keys]
    weak = [k for k in keys if agg[k][1] < args.min_events or agg[k][0] < args.min_volume]

    print(f"{'período':<12} {'volumen':>10} {'suma':>12} {'tasa/media':>11}")
    for k, r in zip(keys, rates):
        flag = "  ← pocos eventos o volumen" if k in weak else ""
        print(f"{k:<12} {agg[k][0]:>10} {agg[k][1]:>12g} {r:>11.4f}{flag}")

    if args.agg or args.granularity == "month":
        q = defaultdict(lambda: [0, 0.0])
        for k in keys:
            q[quarter_of(k)][0] += agg[k][0]
            q[quarter_of(k)][1] += agg[k][1]
        print(f"\n{'trimestre':<12} {'volumen':>10} {'suma':>12} {'tasa/media':>11}")
        for k in sorted(q):
            print(f"{k:<12} {q[k][0]:>10} {q[k][1]:>12g} {q[k][1] / q[k][0] if q[k][0] else 0:>11.4f}")

    total_n = sum(v[0] for v in agg.values())
    total_s = sum(v[1] for v in agg.values())
    mean_rate = statistics.fmean(rates)
    cv = statistics.pstdev(rates) / mean_rate if mean_rate else float("inf")
    trend = slope(rates) * periods_per_year / mean_rate if mean_rate else 0.0
    jumps = []
    for (k0, r0), (k1, r1) in zip(zip(keys, rates), zip(keys[1:], rates[1:])):
        if r0 > 0 and abs(r1 - r0) / r0 > args.max_jump:
            jumps.append(f"{k0}→{k1} {r0:.4f}→{r1:.4f}")

    print(f"\nTotal: volumen {total_n}, suma {total_s:g}, tasa/media global {total_s / total_n:.4f}")
    if skipped:
        print(f"Filas con target vacío o no numérico, ignoradas: {skipped}")
    print(f"Coeficiente de variación de la tasa entre períodos: {cv:.2f}")
    print(f"Tendencia anual relativa de la tasa: {trend:+.1%}")
    print(f"Períodos con menos de {args.min_events:g} eventos o {args.min_volume} filas: {len(weak)}"
          + (f" ({', '.join(weak[:12])})" if weak else ""))
    print(f"Saltos mayores a {args.max_jump:.0%} entre períodos consecutivos: {len(jumps)}"
          + (f" ({'; '.join(jumps[:6])})" if jumps else ""))
    print("MANUAL un salto suele ser un cambio de definición, política o captura: explicarlo antes de particionar")

    if len(weak) * 2 >= len(keys):
        verdict, code = "❌ descartado: la mitad o más de los períodos no tiene eventos suficientes", 1
    elif weak or jumps:
        verdict, code = "⚠️ parcial: indicar qué rango de períodos es viable y por qué", 1
    else:
        verdict, code = "✅ viable", 0
    print("\nVeredicto:", verdict)
    return code


if __name__ == "__main__":
    sys.exit(main())
