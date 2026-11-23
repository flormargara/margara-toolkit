#!/usr/bin/env python3
"""Concentración de la importancia de variables de un modelo.

Un modelo que depende de muy pocas variables es frágil ante cambios de datos y
suele ser señal de leakage. Este chequeo resume la concentración y aplica umbrales.

Entrada: CSV con columnas de variable e importancia (por ejemplo, SHAP medio
absoluto), o JSON {"variable": importancia}.

Uso:
  check_concentration.py importancias.csv
  check_concentration.py importancias.json --max-top1 0.30 --min-n-eff 6

Métricas:
  share_top1/3/5  participación de las 1, 3 y 5 variables principales
  hhi             índice de Herfindahl-Hirschman: suma de participaciones al cuadrado
  hhi_excess      hhi − 1/n (0 = importancia repartida de forma pareja)
  n_eff           número efectivo de variables = 1 / hhi

Los umbrales por defecto son un punto de partida; ajustarlos al problema y
dejarlos escritos en la spec del modelo.

Salida: 0 si pasa; 1 si algún umbral falla. Solo biblioteca estándar.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path


def load(path: Path, name_col: str, value_col: str) -> dict[str, float]:
    if path.suffix.lower() == ".json":
        data = json.loads(path.read_text(encoding="utf-8"))
        return {str(k): abs(float(v)) for k, v in data.items()}
    with path.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        cols = reader.fieldnames or []
        name = name_col if name_col in cols else cols[0]
        value = value_col if value_col in cols else cols[1]
        return {row[name]: abs(float(row[value])) for row in reader if row[value].strip()}


def concentration(imp: dict[str, float]) -> dict:
    total = sum(imp.values())
    if total <= 0:
        raise ValueError("la suma de importancias es 0")
    ranked = sorted(((k, v / total) for k, v in imp.items()), key=lambda kv: kv[1], reverse=True)
    shares = [s for _, s in ranked]
    hhi = sum(s * s for s in shares)
    n = len(shares)
    return {
        "n": n,
        "top": ranked[:5],
        "share_top1": sum(shares[:1]),
        "share_top3": sum(shares[:3]),
        "share_top5": sum(shares[:5]),
        "hhi": hhi,
        "hhi_excess": hhi - 1 / n,
        "n_eff": 1 / hhi,
    }


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("importances")
    p.add_argument("--name-col", default="feature")
    p.add_argument("--value-col", default="importance")
    p.add_argument("--max-top1", type=float, default=0.35, help="Participación máxima de la variable principal")
    p.add_argument("--max-top3", type=float, default=0.70, help="Participación máxima de las 3 principales")
    p.add_argument("--min-n-eff", type=float, default=4.0, help="Número efectivo mínimo de variables")
    args = p.parse_args()

    c = concentration(load(Path(args.importances), args.name_col, args.value_col))

    print(f"variables: {c['n']}")
    print("principales:")
    for name, share in c["top"]:
        print(f"  {share:6.1%}  {name}")
    print(f"share_top1 {c['share_top1']:.1%} | share_top3 {c['share_top3']:.1%} | share_top5 {c['share_top5']:.1%}")
    print(f"hhi {c['hhi']:.4f} | hhi_excess {c['hhi_excess']:.4f} | n_eff {c['n_eff']:.1f}")

    failures = []
    if c["share_top1"] > args.max_top1:
        failures.append(f"la variable principal explica {c['share_top1']:.1%} (> {args.max_top1:.0%})")
    if c["share_top3"] > args.max_top3:
        failures.append(f"las 3 principales explican {c['share_top3']:.1%} (> {args.max_top3:.0%})")
    if c["n_eff"] < args.min_n_eff:
        failures.append(f"número efectivo de variables {c['n_eff']:.1f} (< {args.min_n_eff})")

    if failures:
        print("\n❌ Concentración excesiva:", file=sys.stderr)
        for f in failures:
            print(f"  - {f}", file=sys.stderr)
        print("Revisar leakage en las variables principales (ml-foundations/knowledge/02-leakage.md) antes de aceptar el modelo.", file=sys.stderr)
        return 1
    print("\n✅ Concentración dentro de los umbrales")
    return 0


if __name__ == "__main__":
    sys.exit(main())
