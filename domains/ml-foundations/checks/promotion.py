#!/usr/bin/env python3
"""Regla de promoción: champion, recalibrado o challenger.

Compara los candidatos sobre la misma cohorte madura que ninguno usó para entrenar
(ver knowledge/06-monitoreo.md, "Promoción") y aplica la regla:

  1. El challenger gana si su AUC supera al del champion por al menos --min-margin,
     o si el intervalo bootstrap pareado de la diferencia excluye el cero
     (con --require both, hacen falta las dos cosas), y además su error de
     calibración no es peor que el del champion en más de --cal-tolerance.
  2. Si no, el recalibrado gana si reduce el error de calibración del champion en
     al menos --min-cal-gain sin perder AUC más allá de --cal-tolerance.
  3. En cualquier otro caso, o con datos insuficientes, se queda el champion.

Entrada: CSV con una fila por entidad de la cohorte, el target binario (0/1) y una
columna de probabilidad por candidato. El recalibrado es opcional. Las filas con algún
valor vacío se descartan y se informan.

Error de calibración: promedio ponderado de |tasa observada − probabilidad media| en
--bins grupos de igual tamaño ordenados por la probabilidad de cada candidato.

Uso:
  promotion.py cohorte.csv --champion score_v3 --challenger score_v4
  promotion.py cohorte.csv --champion v3 --recalibrated v3_recal --challenger v4 \\
      --min-margin 0.01 --where grupo=control --json decision.json

Salida: imprime la decisión y sale con 0. Sale con 2 si el archivo o las columnas
no existen. Solo biblioteca estándar.
"""

from __future__ import annotations

import argparse
import csv
import json
import random
import sys
from pathlib import Path


def auc(y: list[int], p: list[float]) -> float:
    """AUC por rangos (Mann-Whitney), con empates promediados."""
    order = sorted(range(len(p)), key=p.__getitem__)
    ranks = [0.0] * len(p)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and p[order[j + 1]] == p[order[i]]:
            j += 1
        r = (i + j) / 2 + 1
        for k in range(i, j + 1):
            ranks[order[k]] = r
        i = j + 1
    pos = sum(y)
    neg = len(y) - pos
    rank_sum = sum(r for r, t in zip(ranks, y) if t == 1)
    return (rank_sum - pos * (pos + 1) / 2) / (pos * neg)


def calibration_error(y: list[int], p: list[float], bins: int) -> float:
    order = sorted(range(len(p)), key=p.__getitem__)
    n = len(order)
    total = 0.0
    for b in range(bins):
        idx = order[b * n // bins:(b + 1) * n // bins]
        if not idx:
            continue
        obs = sum(y[i] for i in idx) / len(idx)
        pred = sum(p[i] for i in idx) / len(idx)
        total += len(idx) * abs(obs - pred)
    return total / n


def bootstrap_diff(y, a, b, n_boot: int, seed: int, level: float) -> tuple[float, float]:
    """Intervalo percentil de AUC(b) − AUC(a), remuestreando las mismas filas para ambos."""
    rng = random.Random(seed)
    n = len(y)
    diffs = []
    for _ in range(n_boot):
        idx = [rng.randrange(n) for _ in range(n)]
        yy = [y[i] for i in idx]
        if 0 < sum(yy) < n:
            diffs.append(auc(yy, [b[i] for i in idx]) - auc(yy, [a[i] for i in idx]))
    diffs.sort()
    lo = diffs[int((1 - level) / 2 * len(diffs))]
    hi = diffs[min(len(diffs) - 1, int((1 + level) / 2 * len(diffs)))]
    return lo, hi


def load(path: Path, target: str, cols: list[str], where: list[str]):
    filters = []
    for w in where:
        k, _, v = w.partition("=")
        filters.append((k, v))
    with path.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        header = reader.fieldnames or []
        missing = [c for c in [target, *cols, *(k for k, _ in filters)] if c not in header]
        if missing:
            raise KeyError(", ".join(missing))
        y, scores, dropped = [], {c: [] for c in cols}, 0
        for row in reader:
            if any(row[k] != v for k, v in filters):
                continue
            values = [row[target], *(row[c] for c in cols)]
            if any(v is None or not v.strip() for v in values):
                dropped += 1
                continue
            y.append(int(float(row[target])))
            for c in cols:
                scores[c].append(float(row[c]))
    return y, scores, dropped


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("cohort")
    p.add_argument("--target", default="target")
    p.add_argument("--champion", required=True, help="Columna del modelo vigente")
    p.add_argument("--challenger", required=True, help="Columna del modelo reentrenado")
    p.add_argument("--recalibrated", help="Columna del vigente recalibrado (opcional)")
    p.add_argument("--where", action="append", default=[], help="Filtro columna=valor, repetible")
    p.add_argument("--min-margin", type=float, default=0.01, help="Mejora mínima de AUC del challenger")
    p.add_argument("--require", choices=["either", "both"], default="either",
                   help="either: margen o intervalo; both: margen e intervalo")
    p.add_argument("--cal-tolerance", type=float, default=0.005,
                   help="Empeoramiento máximo aceptado del error de calibración (y del AUC del recalibrado)")
    p.add_argument("--min-cal-gain", type=float, default=0.002, help="Mejora mínima de calibración del recalibrado")
    p.add_argument("--bins", type=int, default=10)
    p.add_argument("--n-boot", type=int, default=300)
    p.add_argument("--level", type=float, default=0.95)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--min-events", type=int, default=30, help="Eventos y no eventos mínimos en la cohorte")
    p.add_argument("--json", help="Escribe la decisión y las métricas en este archivo")
    args = p.parse_args()

    cols = [args.champion, args.challenger] + ([args.recalibrated] if args.recalibrated else [])
    try:
        y, s, dropped = load(Path(args.cohort), args.target, cols, args.where)
    except FileNotFoundError:
        print(f"ERROR: no existe {args.cohort}", file=sys.stderr)
        return 2
    except KeyError as e:
        print(f"ERROR: faltan columnas: {e.args[0]}", file=sys.stderr)
        return 2

    n, events = len(y), sum(y)
    print(f"cohorte: {n} filas, {events} eventos" + (f", {dropped} descartadas por valores vacíos" if dropped else ""))
    out = {"n": n, "events": events, "dropped": dropped, "metrics": {}}

    def finish(decision: str, reason: str) -> int:
        out["decision"], out["reason"] = decision, reason
        print(f"\nDECISIÓN: {decision} — {reason}")
        if args.json:
            Path(args.json).write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
        return 0

    if min(events, n - events) < args.min_events:
        return finish("champion", f"datos insuficientes: hacen falta al menos {args.min_events} eventos y no eventos")

    m = {c: {"auc": auc(y, s[c]), "cal": calibration_error(y, s[c], args.bins)} for c in cols}
    out["metrics"] = m
    print(f"\n{'candidato':<24}{'AUC':>8}{'error calib.':>14}")
    for role, c in [("champion", args.champion), ("recalibrado", args.recalibrated), ("challenger", args.challenger)]:
        if c:
            print(f"{role + ' (' + c + ')':<24}{m[c]['auc']:>8.4f}{m[c]['cal']:>14.4f}")

    ch, cl = m[args.champion], m[args.challenger]
    diff = cl["auc"] - ch["auc"]
    lo, hi = bootstrap_diff(y, s[args.champion], s[args.challenger], args.n_boot, args.seed, args.level)
    out["auc_diff"], out["auc_diff_ci"] = diff, [lo, hi]
    print(f"\nAUC challenger − champion: {diff:+.4f}  IC {args.level:.0%} [{lo:+.4f}, {hi:+.4f}]")

    by_margin, by_ci = diff >= args.min_margin, lo > 0
    better = (by_margin and by_ci) if args.require == "both" else (by_margin or by_ci)
    cal_ok = cl["cal"] <= ch["cal"] + args.cal_tolerance
    if better and cal_ok:
        why = " y ".join(x for x, ok in [(f"margen ≥ {args.min_margin}", by_margin), ("IC sin el cero", by_ci)] if ok)
        return finish("challenger", f"mejora el AUC ({why}) sin empeorar la calibración")
    if better:
        print(f"el challenger mejora el AUC pero empeora la calibración: {cl['cal']:.4f} vs {ch['cal']:.4f}")
    else:
        print(f"el challenger no supera el margen mínimo ({args.min_margin}) y su IC incluye el cero"
              if args.require == "either" else "el challenger no cumple margen e IC a la vez")

    if args.recalibrated:
        rc = m[args.recalibrated]
        if rc["cal"] <= ch["cal"] - args.min_cal_gain and rc["auc"] >= ch["auc"] - args.cal_tolerance:
            return finish("recalibrado", f"reduce el error de calibración de {ch['cal']:.4f} a {rc['cal']:.4f}")
        print("el recalibrado no reduce la calibración lo suficiente")

    return finish("champion", "ningún candidato cumple la regla")


if __name__ == "__main__":
    sys.exit(main())
