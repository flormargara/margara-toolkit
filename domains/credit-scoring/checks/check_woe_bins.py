#!/usr/bin/env python3
"""Chequeo de un binning WoE antes de usarlo en una regresión logística.

Entrada: una tabla de binning en CSV, una fila por variable y bin, en el orden de los
bins (de menor a mayor valor). Lo que exporta cualquier herramienta de binning sirve
si tiene variable, bin, cantidad total y cantidad de malos (o buenos y malos). Usar
la tabla calculada en train, solo con buenos y malos.

Uso:
  check_woe_bins.py binning.csv
  check_woe_bins.py binning.csv --var-col variable --bin-col bin --n-col count --bads-col event
  check_woe_bins.py binning.csv --goods-col non_event --bads-col event \
      --allow-nonmonotonic edad --allow-high-iv dias_atraso_max

WoE = ln(% de buenos / % de malos): un WoE más alto es menos riesgo.

Chequeos por variable:
  1. Bins vacíos de una clase: un bin sin buenos o sin malos da WoE infinito.       FAIL
  2. Tamaño: cada bin regular con al menos --min-share de la población.           FAIL
     Bins especiales (faltantes, valores especiales) por debajo del mínimo.       WARN
  3. Malos por bin: al menos --min-bads en cada bin regular.                       FAIL
  4. Monotonía: el WoE de los bins regulares es monótono (salvo las variables
     listadas en --allow-nonmonotonic, que necesitan justificación escrita).      FAIL
     Bins contiguos con WoE casi igual (|dif| < --min-woe-gap) conviene unirlos.  WARN
  5. IV > --max-iv: sospechoso de leakage (salvo --allow-high-iv).                 FAIL
     IV < --min-iv: sin poder predictivo.                                         WARN

Los bins especiales se detectan por nombre con --special-regex y quedan fuera de la
monotonía. Salida: 0 si todo pasa; 1 si algún chequeo falla. Solo biblioteca estándar.
"""

from __future__ import annotations

import argparse
import csv
import math
import re
import sys
from collections import OrderedDict

DEFAULT_SPECIAL = r"(?i)^\s*(missing|nan|null|none|na|faltante|sin dato|special|especial)\b"


def to_num(text: str, where: str) -> float:
    try:
        return float(text)
    except (TypeError, ValueError):
        raise SystemExit(f"valor no numérico en {where}: {text!r}")


def names(text: str) -> set[str]:
    return {x.strip() for x in (text or "").split(",") if x.strip()}


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("table")
    p.add_argument("--var-col", default="variable")
    p.add_argument("--bin-col", default="bin")
    p.add_argument("--n-col", default="n", help="Cantidad total del bin (si no se pasa --goods-col)")
    p.add_argument("--goods-col", help="Cantidad de buenos (alternativa a --n-col)")
    p.add_argument("--bads-col", default="bads")
    p.add_argument("--special-regex", default=DEFAULT_SPECIAL)
    p.add_argument("--min-share", type=float, default=0.05)
    p.add_argument("--min-bads", type=int, default=30)
    p.add_argument("--min-woe-gap", type=float, default=0.05)
    p.add_argument("--min-iv", type=float, default=0.02)
    p.add_argument("--max-iv", type=float, default=0.5)
    p.add_argument("--allow-nonmonotonic", default="", help="Variables con relación no monótona justificada")
    p.add_argument("--allow-high-iv", default="", help="Variables con IV alto revisado y justificado")
    args = p.parse_args()

    special = re.compile(args.special_regex)
    allow_nm, allow_iv = names(args.allow_nonmonotonic), names(args.allow_high_iv)

    variables: "OrderedDict[str, list[dict]]" = OrderedDict()
    with open(args.table, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        cols = reader.fieldnames or []
        needed = [args.var_col, args.bin_col, args.bads_col, args.goods_col or args.n_col]
        missing = [c for c in needed if c not in cols]
        if missing:
            raise SystemExit(f"columnas ausentes en {args.table}: {', '.join(missing)}")
        for i, row in enumerate(reader, start=2):
            name = row[args.var_col].strip()
            label = row[args.bin_col].strip()
            if label.lower() in {"total", "totals"}:
                continue
            bads = to_num(row[args.bads_col], f"línea {i}")
            goods = (to_num(row[args.goods_col], f"línea {i}") if args.goods_col
                     else to_num(row[args.n_col], f"línea {i}") - bads)
            if goods < 0:
                raise SystemExit(f"línea {i}: más malos que total en {name} / {label}")
            variables.setdefault(name, []).append(
                {"bin": label, "goods": goods, "bads": bads, "special": bool(special.search(label))}
            )

    if not variables:
        print("tabla vacía", file=sys.stderr)
        return 1

    results: list[tuple[str, str, str]] = []
    summary = []
    for name, bins in variables.items():
        tg = sum(b["goods"] for b in bins)
        tb = sum(b["bads"] for b in bins)
        total = tg + tb
        tag = f"[{name}] "
        if not tg or not tb:
            results.append(("FAIL", tag, "la variable no tiene buenos o no tiene malos"))
            continue

        iv, infinite = 0.0, False
        for b in bins:
            if not b["goods"] or not b["bads"]:
                infinite = True
                results.append(("FAIL", tag, f"bin {b['bin']!r}: {int(b['goods'])} buenos y "
                                            f"{int(b['bads'])} malos; WoE infinito, unirlo con un vecino"))
                b["woe"] = None
                continue
            pg, pb = b["goods"] / tg, b["bads"] / tb
            b["woe"] = math.log(pg / pb)
            iv += (pg - pb) * b["woe"]

        for b in bins:
            share = (b["goods"] + b["bads"]) / total
            if share < args.min_share:
                results.append(("WARN" if b["special"] else "FAIL", tag,
                                f"bin {b['bin']!r}: {share:.1%} de la población < {args.min_share:.0%}"
                                + (" (bin especial)" if b["special"] else "")))
            if not b["special"] and b["bads"] < args.min_bads:
                results.append(("FAIL", tag, f"bin {b['bin']!r}: {int(b['bads'])} malos < {args.min_bads}"))

        regular = [b for b in bins if not b["special"] and b["woe"] is not None]
        woes = [b["woe"] for b in regular]
        diffs = [y - x for x, y in zip(woes, woes[1:])]
        direction = "—"
        if diffs:
            up, down = all(d >= 0 for d in diffs), all(d <= 0 for d in diffs)
            if up or down:
                direction = "el riesgo baja al subir el bin" if up else "el riesgo sube al subir el bin"
                results.append(("OK", tag, f"monotonía: {direction}"))
            elif name in allow_nm:
                direction = "no monótona (justificada)"
                results.append(("WARN", tag, "WoE no monótono; permitido por --allow-nonmonotonic, "
                                             "dejar la justificación escrita"))
            else:
                direction = "no monótona"
                seq = " → ".join(f"{w:+.2f}" for w in woes)
                results.append(("FAIL", tag, f"WoE no monótono: {seq}"))
            for (a, b_), d in zip(zip(regular, regular[1:]), diffs):
                if abs(d) < args.min_woe_gap:
                    results.append(("WARN", tag, f"bins {a['bin']!r} y {b_['bin']!r} con WoE casi igual "
                                                 f"(dif {d:+.3f}); evaluar unirlos"))

        if not infinite:
            if iv > args.max_iv:
                results.append(("WARN" if name in allow_iv else "FAIL", tag,
                                f"IV {iv:.3f} > {args.max_iv}: revisar leakage"
                                + (" (revisado, --allow-high-iv)" if name in allow_iv else "")))
            elif iv < args.min_iv:
                results.append(("WARN", tag, f"IV {iv:.3f} < {args.min_iv}: sin poder predictivo"))
        summary.append((name, len(bins), None if infinite else iv, direction))

    print(f"{'variable':<32}{'bins':>6}{'IV':>9}  dirección")
    for name, nb, iv, direction in summary:
        print(f"{name[:31]:<32}{nb:>6}{'—' if iv is None else f'{iv:.3f}':>9}  {direction}")
    print()
    for status, tag, msg in results:
        if status != "OK":
            print(f"{status:<5} {tag}{msg}")
    oks = sum(1 for s, _, _ in results if s == "OK")
    print(f"OK    {oks} variables con WoE monótono")
    print("MANUAL confirmar que la dirección del riesgo de cada variable es la que espera el negocio")
    print("MANUAL confirmar que los cortes se ajustaron solo con train (y sin indeterminados)")

    failed = any(s == "FAIL" for s, _, _ in results)
    print("\nVeredicto:", "❌ el binning no cumple" if failed else "✅ binning verificado")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
