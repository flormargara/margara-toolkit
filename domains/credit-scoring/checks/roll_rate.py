#!/usr/bin/env python3
"""Análisis de roll rate para elegir qué tramo de atraso es "malo".

Entrada: un CSV en formato largo, una fila por cuenta y mes, con los días de atraso
(o el tramo ya asignado) a fin de mes.

Uso:
  roll_rate.py historia.csv --id-col cuenta --period-col mes --dpd-col dias_atraso
  roll_rate.py historia.csv --bins 0,1,31,61,91 --obs-months 6 --perf-months 12 --bad-from 61-90
  roll_rate.py historia.csv --bucket-col tramo --order "al dia,1-30,31-60,61-90,90+"

Tramos: con --dpd-col, --bins da el límite inferior de cada tramo (0,1,31,61,91 →
0, 1-30, 31-60, 61-90, 91+). Con --bucket-col, --order da los tramos de menor a mayor
atraso. --default-bucket es el evento de pérdida (por defecto, el peor tramo).

Enfoque 1 — peor tramo y resultado posterior. Para cada cuenta y cada mes de
observación s, peor tramo en los --obs-months meses hasta s y si llega a
--default-bucket en los --perf-months meses siguientes. Solo meses s con la ventana de
desempeño completa. Clasificación de cada tramo:
  malo           tasa de default >= --bad-threshold (0.25 por defecto)
  bueno          tasa de default <= promedio de la cartera
  indeterminado  el resto

Enfoque 2 — matriz de transición mes a mes. El "punto de no retorno" es el primer
tramo con atraso en el que es más probable empeorar que quedarse o curarse.

Con --bad-from <tramo> se verifica la definición propuesta (ese tramo y los peores
son "malo"):
  FAIL  si el tramo propuesto, o uno peor, sale "bueno" en el enfoque 1.
  WARN  si sale "indeterminado", si un tramo menos grave ya es "malo", o si no coincide
        con el punto de no retorno del enfoque 2.
Sin --bad-from, solo informa y sale con 0. Solo biblioteca estándar.
"""

from __future__ import annotations

import argparse
import csv
import sys
from collections import defaultdict
from datetime import datetime

NULLS = {"", "na", "nan", "null", "none"}


def month_index(text: str) -> int:
    text = text.strip()
    for fmt in ("%Y-%m-%d", "%Y-%m-%d %H:%M:%S", "%Y%m%d", "%Y-%m", "%Y%m", "%d/%m/%Y"):
        try:
            d = datetime.strptime(text, fmt)
            return d.year * 12 + d.month - 1
        except ValueError:
            continue
    raise SystemExit(f"fecha no reconocida: {text!r}")


def month_label(idx: int) -> str:
    return f"{idx // 12}-{idx % 12 + 1:02d}"


def bin_labels(bounds: list[int]) -> list[str]:
    labels = []
    for i, lo in enumerate(bounds):
        if i + 1 < len(bounds):
            hi = bounds[i + 1] - 1
            labels.append(str(lo) if hi == lo else f"{lo}-{hi}")
        else:
            labels.append(f"{lo}+")
    return labels


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("history")
    p.add_argument("--id-col", default="id")
    p.add_argument("--period-col", default="periodo")
    p.add_argument("--dpd-col", help="Días de atraso a fin de mes")
    p.add_argument("--bins", default="0,1,31,61,91", help="Límite inferior de cada tramo (con --dpd-col)")
    p.add_argument("--bucket-col", help="Tramo ya asignado (alternativa a --dpd-col)")
    p.add_argument("--order", help="Tramos de menor a mayor atraso (con --bucket-col)")
    p.add_argument("--default-bucket", help="Tramo que cuenta como pérdida (por defecto, el peor)")
    p.add_argument("--obs-months", type=int, default=6)
    p.add_argument("--perf-months", type=int, default=12)
    p.add_argument("--step", type=int, default=1, help="Cada cuántos meses tomar un mes de observación")
    p.add_argument("--bad-threshold", type=float, default=0.25)
    p.add_argument("--min-n", type=int, default=100, help="Mínimo de observaciones para clasificar un tramo")
    p.add_argument("--bad-from", help="Definición propuesta: primer tramo considerado malo")
    args = p.parse_args()

    if bool(args.dpd_col) == bool(args.bucket_col):
        raise SystemExit("indicar --dpd-col o --bucket-col (uno de los dos)")
    if args.dpd_col:
        bounds = sorted(int(x) for x in args.bins.split(",") if x.strip())
        labels = bin_labels(bounds)
    else:
        if not args.order:
            raise SystemExit("--bucket-col requiere --order")
        labels = [x.strip() for x in args.order.split(",") if x.strip()]
    pos = {b: i for i, b in enumerate(labels)}
    default_bucket = args.default_bucket or labels[-1]
    if default_bucket not in pos:
        raise SystemExit(f"--default-bucket {default_bucket!r} no es un tramo: {', '.join(labels)}")
    if args.bad_from and args.bad_from not in pos:
        raise SystemExit(f"--bad-from {args.bad_from!r} no es un tramo: {', '.join(labels)}")
    d_pos = pos[default_bucket]

    hist: dict[str, dict[int, int]] = defaultdict(dict)
    with open(args.history, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        col = args.dpd_col or args.bucket_col
        missing = [c for c in (args.id_col, args.period_col, col) if c not in (reader.fieldnames or [])]
        if missing:
            raise SystemExit(f"columnas ausentes en {args.history}: {', '.join(missing)}")
        for row in reader:
            raw = row[col].strip()
            if raw.lower() in NULLS:
                continue
            if args.dpd_col:
                dpd = float(raw)
                b = max(i for i, lo in enumerate(bounds) if dpd >= lo) if dpd >= bounds[0] else 0
            else:
                if raw not in pos:
                    raise SystemExit(f"tramo {raw!r} fuera de --order")
                b = pos[raw]
            m = month_index(row[args.period_col])
            key = row[args.id_col].strip()
            hist[key][m] = max(b, hist[key].get(m, 0))

    if not hist:
        print("historia vacía", file=sys.stderr)
        return 1
    first = min(min(h) for h in hist.values())
    last = max(max(h) for h in hist.values())

    # Enfoque 2: transiciones mes a mes
    trans = [[0] * len(labels) for _ in labels]
    for h in hist.values():
        for m, b in h.items():
            if m + 1 in h:
                trans[b][h[m + 1]] += 1

    print(f"Cuentas: {len(hist)}; meses: {month_label(first)} a {month_label(last)}\n")
    print("Matriz de transición (fila: tramo en t; columnas: % en t+1)")
    w = max(9, max(len(x) for x in labels) + 2)
    print(f"{'':<{w}}" + "".join(f"{x:>{w}}" for x in labels) + f"{'n':>9}{'empeora':>9}")
    no_return = None
    for i, row in enumerate(trans):
        n = sum(row)
        if not n:
            print(f"{labels[i]:<{w}}" + f"{'—':>{w}}" * len(labels) + f"{0:>9}")
            continue
        worse = sum(row[i + 1:]) / n
        print(f"{labels[i]:<{w}}" + "".join(f"{c / n:>{w}.1%}" for c in row) + f"{n:>9}{worse:>9.1%}")
        if no_return is None and i > 0 and i < len(labels) - 1 and worse > 0.5 and n >= args.min_n:
            no_return = labels[i]
    print(f"\nPunto de no retorno (enfoque 2): {no_return or 'ninguno'}\n")

    # Enfoque 1: peor tramo en observación → default en desempeño
    counts = [[0, 0] for _ in labels]   # [n, defaults]
    for h in hist.values():
        months = sorted(h)
        for s in range(months[0], months[-1] + 1, args.step):
            if s not in h or s + args.perf_months > last or s - args.obs_months + 1 < first:
                continue
            worst = max(h.get(m, 0) for m in range(s - args.obs_months + 1, s + 1))
            if worst >= d_pos:
                continue
            hit = any(h.get(m, 0) >= d_pos for m in range(s + 1, s + args.perf_months + 1))
            counts[worst][0] += 1
            counts[worst][1] += hit

    total_n = sum(c[0] for c in counts)
    if not total_n:
        print("no hay meses de observación con ventana completa: acortar --obs-months o --perf-months",
              file=sys.stderr)
        return 1
    avg = sum(c[1] for c in counts) / total_n
    print(f"Enfoque 1: peor tramo en {args.obs_months} meses → llega a {default_bucket} en los "
          f"{args.perf_months} siguientes")
    print(f"{'tramo':<{w}}{'n':>9}{'defaults':>10}{'tasa':>9}  clase")
    klass: dict[int, str] = {}
    for i in range(d_pos):
        n, d = counts[i]
        if n < args.min_n:
            klass[i] = "insuficiente"
            print(f"{labels[i]:<{w}}{n:>9}{d:>10}{(d / n if n else 0):>9.1%}  datos insuficientes")
            continue
        rate = d / n
        klass[i] = "malo" if rate >= args.bad_threshold else "bueno" if rate <= avg else "indeterminado"
        print(f"{labels[i]:<{w}}{n:>9}{d:>10}{rate:>9.1%}  {klass[i]}")
    print(f"{'cartera':<{w}}{total_n:>9}{sum(c[1] for c in counts):>10}{avg:>9.1%}\n")

    results: list[tuple[str, str]] = []
    rated = [i for i in range(d_pos) if klass.get(i) not in (None, "insuficiente")]
    for a, b in zip(rated, rated[1:]):
        ra, rb = counts[a][1] / counts[a][0], counts[b][1] / counts[b][0]
        if rb < ra:
            results.append(("WARN", f"la tasa de default baja de {labels[a]} ({ra:.1%}) a {labels[b]} ({rb:.1%})"))

    if args.bad_from:
        bf = pos[args.bad_from]
        if bf >= d_pos:
            results.append(("OK", f"--bad-from {args.bad_from} coincide con el evento de pérdida"))
        else:
            k = klass.get(bf)
            if k == "malo":
                results.append(("OK", f"{args.bad_from} sale malo en el enfoque 1"))
            elif k == "bueno":
                results.append(("FAIL", f"{args.bad_from} sale bueno en el enfoque 1: la definición es demasiado laxa"))
            elif k == "indeterminado":
                results.append(("WARN", f"{args.bad_from} sale indeterminado: tasa entre el promedio "
                                        f"({avg:.1%}) y {args.bad_threshold:.0%}"))
            else:
                results.append(("WARN", f"{args.bad_from} sin datos suficientes para clasificarlo"))
            for i in range(bf + 1, d_pos):
                if klass.get(i) == "bueno":
                    results.append(("FAIL", f"{labels[i]}, peor que {args.bad_from}, sale bueno"))
        for i in range(min(bf, d_pos)):
            if klass.get(i) == "malo":
                results.append(("WARN", f"{labels[i]}, menos grave que {args.bad_from}, ya sale malo: "
                                        "evaluar adelantar la definición"))
                break
        if no_return and no_return != args.bad_from:
            results.append(("WARN", f"el punto de no retorno del enfoque 2 es {no_return}, no {args.bad_from}"))

    for status, msg in results:
        print(f"{status:<5} {msg}")
    print("MANUAL reportar la matriz y la decisión en la ficha del modelo; comparar contra una definición alternativa")

    failed = any(s == "FAIL" for s, _ in results)
    if args.bad_from:
        warned = any(s == "WARN" for s, _ in results)
        print("\nVeredicto:", "❌ la definición propuesta no se sostiene" if failed
              else "⚠️ requiere revisión: justificar la definición frente a las advertencias" if warned
              else "✅ la definición propuesta es consistente con el roll rate")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
