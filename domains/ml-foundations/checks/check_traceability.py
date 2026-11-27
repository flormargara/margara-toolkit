#!/usr/bin/env python3
"""Cobertura de la cadena de trazabilidad: qué parte de los registros sobrevive cada salto.

Mide, para cada salto de la cadena entrada → predicción → decisión → acción →
resultado, qué porcentaje de registros encuentra su par en la tabla siguiente, por
período y por segmento (ver knowledge/08-trazabilidad.md). Cada tabla es un CSV.

Uso:
  check_traceability.py \\
      --step pred=predicciones.csv --step dec=decisiones.csv --step res=resultados.csv \\
      --hop pred.id_prediccion=dec.id_prediccion \\
      --hop dec.id_decision=res.id_decision \\
      --period pred.fecha_prediccion --segment pred.canal --min-coverage 0.95

  Una clave compuesta se escribe con comas: --hop pred.id,fecha=dec.id,fecha

Cobertura de un salto: registros del lado "desde" con al menos un par en el lado
"hasta", sobre el total del lado "desde". Cobertura acumulada: registros del primer
paso que llegan hasta ese salto. Los saltos van en cadena: cada uno sale del paso
donde terminó el anterior. Por período y segmento (que salen del primer paso), la
cobertura se cuenta sobre los registros del primer paso que llegaron a "desde".

Chequeos:
  1. Cobertura de cada salto, total (sobre los períodos maduros) y en cada
     período y segmento con al menos
     --min-rows registros, mayor o igual que --min-coverage.                FAIL
     Celdas con menos de --min-rows registros.                              no se evalúan
  2. Períodos posteriores a --mature-until (el resultado todavía no llegó)
     se informan pero no se evalúan.
  3. Claves vacías en el lado "desde".                                      WARN
  4. Claves repetidas en el lado "hasta": el join multiplica filas.         WARN
  5. Claves sin par que sí lo encontrarían normalizando el formato
     (espacios, mayúsculas, ceros a la izquierda, "123.0" vs "123").        FAIL

Con --out, escribe la cobertura por salto, período y segmento en un CSV, para
publicarla como indicador.

Salida: 0 si todo pasa; 1 si algún chequeo falla; 2 si una entrada no se puede leer.
Solo biblioteca estándar.
"""

from __future__ import annotations

import argparse
import csv
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path


def parse_ref(text: str) -> tuple[str, list[str]]:
    step, _, cols = text.partition(".")
    if not cols:
        raise ValueError(f"se esperaba paso.columna: {text!r}")
    return step, [c.strip() for c in cols.split(",")]


def norm(value: str) -> str:
    v = value.strip().lower()
    if re.fullmatch(r"-?\d+(\.0+)?", v):
        v = str(int(float(v)))
    return v.lstrip("0") or v


def period_of(value: str, grain: str) -> str:
    v = value.strip()
    return {"month": v[:7], "day": v[:10], "year": v[:4]}.get(grain, v)


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--step", action="append", required=True, help="nombre=archivo.csv, en el orden de la cadena")
    p.add_argument("--hop", action="append", required=True, help="desde.clave=hasta.clave")
    p.add_argument("--period", help="paso.columna de fecha del primer paso")
    p.add_argument("--period-grain", choices=["month", "day", "year", "raw"], default="month")
    p.add_argument("--segment", help="paso.columna de segmento del primer paso")
    p.add_argument("--min-coverage", type=float, default=0.95)
    p.add_argument("--min-rows", type=int, default=100, help="Registros mínimos para evaluar una celda")
    p.add_argument("--mature-until", help="Último período cuyo resultado ya llegó (mismo formato que el período)")
    p.add_argument("--out", help="CSV con la cobertura por salto, período y segmento")
    args = p.parse_args()

    try:
        steps: dict[str, list[dict]] = {}
        for s in args.step:
            name, _, path = s.partition("=")
            with open(path, newline="", encoding="utf-8") as fh:
                steps[name] = list(csv.DictReader(fh))
        hops = []
        for h in args.hop:
            left, _, right = h.partition("=")
            (a, ka), (b, kb) = parse_ref(left), parse_ref(right)
            for step, cols in ((a, ka), (b, kb)):
                if step not in steps:
                    raise ValueError(f"el paso {step!r} no está en --step")
                if steps[step] and any(c not in steps[step][0] for c in cols):
                    raise ValueError(f"{step} no tiene la columna {', '.join(c for c in cols if c not in steps[step][0])}")
            if hops and a != hops[-1][2]:
                raise ValueError(f"los saltos van en cadena: {h!r} tiene que salir de {hops[-1][2]!r}")
            hops.append((a, ka, b, kb))
        first = hops[0][0]
        attrs = {}
        for flag in ("period", "segment"):
            ref = getattr(args, flag)
            if ref:
                step, cols = parse_ref(ref)
                if step != first:
                    raise ValueError(f"--{flag} tiene que ser del primer paso ({first})")
                if steps[first] and cols[0] not in steps[first][0]:
                    raise ValueError(f"{first} no tiene la columna {cols[0]}")
                attrs[flag] = cols[0]
    except (OSError, ValueError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2

    origin = steps[first]

    def cell(i: int) -> tuple[str, str]:
        row = origin[i]
        per = period_of(row[attrs["period"]], args.period_grain) if "period" in attrs else "todo"
        return per, row[attrs["segment"]] if "segment" in attrs else "todo"

    # reached[j] = filas del primer paso que llegan a la fila j del paso actual
    reached = {j: {j} for j in range(len(origin))}
    results: list[tuple[str, str]] = []
    report = []
    for a, ka, b, kb in hops:
        hop = f"{a} → {b}"
        rows_a, rows_b = steps[a], steps[b]
        key = lambda r, cols: tuple(r[c] for c in cols)
        index = defaultdict(list)
        for j, r in enumerate(rows_b):
            index[key(r, kb)].append(j)
        norm_keys = {tuple(norm(v) for v in k) for k in index}

        empty = sum(1 for r in rows_a if all(not v.strip() for v in key(r, ka)))
        dups = sum(1 for k, js in index.items() if len(js) > 1 and any(v.strip() for v in k))
        matched_a, fixable = 0, 0
        new_reached: dict[int, set[int]] = defaultdict(set)
        before = set().union(*reached.values()) if reached else set()
        for i, r in enumerate(rows_a):
            k = key(r, ka)
            targets = index.get(k, [])
            if targets:
                matched_a += 1
            elif any(v.strip() for v in k) and tuple(norm(v) for v in k) in norm_keys:
                fixable += 1
            for j in targets:
                new_reached[j] |= reached.get(i, set())
        reached = new_reached
        survivors = set().union(*reached.values()) if reached else set()
        # por celda: registros del primer paso que llegan a "desde" y cuántos de ellos pasan a "hasta"
        hop_cells: dict[tuple[str, str], list[int]] = defaultdict(lambda: [0, 0])
        for o in before:
            c = hop_cells[cell(o)]
            c[0] += 1
            c[1] += o in survivors
        origin_cells = Counter(cell(o) for o in range(len(origin)))

        total = len(rows_a)
        cov = matched_a / total if total else 0.0
        print(f"\n{hop} ({'+'.join(ka)} = {'+'.join(kb)})")
        print(f"  cobertura del salto: {matched_a}/{total} = {cov:.1%} · acumulada desde {first}: "
              f"{len(survivors)}/{len(origin)} = {len(survivors) / len(origin):.1%}" if origin else "")
        if empty:
            results.append(("WARN", f"{hop}: {empty} claves vacías en {a}"))
        if dups:
            results.append(("WARN", f"{hop}: {dups} claves repetidas en {b}; el join multiplica filas"))
        if fixable:
            results.append(("FAIL", f"{hop}: {fixable} claves sin par lo encontrarían normalizando el formato "
                                    f"(espacios, mayúsculas, ceros, decimales)"))

        if attrs:
            print(f"  {'período':<10}{'segmento':<14}{'desde':>8}{'con par':>9}{'cobertura':>11}")
        for (per, seg), (n, m) in sorted(hop_cells.items()):
            c = m / n if n else 0.0
            immature = bool(args.mature_until and "period" in attrs and per > args.mature_until)
            status = "inmaduro" if immature else ("sin evaluar" if n < args.min_rows else
                                                  ("FAIL" if c < args.min_coverage else "OK"))
            if attrs:
                print(f"  {per:<10}{seg:<14}{n:>8}{m:>9}{c:>10.1%}  {status}")
            if status == "FAIL":
                results.append(("FAIL", f"{hop}: período {per}, segmento {seg}: cobertura {c:.1%}"))
            report.append({"salto": hop, "periodo": per, "segmento": seg, "desde": n, "con_par": m,
                           "cobertura": round(c, 4),
                           "acumulada": round(m / origin_cells[(per, seg)], 4), "estado": status})

        mature = [(n, m) for (per, _), (n, m) in hop_cells.items()
                  if not (args.mature_until and "period" in attrs and per > args.mature_until)]
        n_mat, m_mat = sum(n for n, _ in mature), sum(m for _, m in mature)
        if args.mature_until and "period" in attrs:
            print(f"  cobertura de los períodos maduros (hasta {args.mature_until}): "
                  f"{m_mat}/{n_mat} = {m_mat / n_mat:.1%}" if n_mat else "  sin períodos maduros")
        if n_mat >= args.min_rows and m_mat / n_mat < args.min_coverage:
            results.append(("FAIL", f"{hop}: cobertura {m_mat / n_mat:.1%} menor que {args.min_coverage:.0%}"))

    if args.out:
        with open(args.out, "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=list(report[0]) if report else ["salto"])
            w.writeheader()
            w.writerows(report)

    print()
    for level, msg in results:
        print(f"{level:<5} {msg}")
    failed = any(level == "FAIL" for level, _ in results)
    if not failed:
        print(f"OK    todos los saltos con cobertura ≥ {args.min_coverage:.0%}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
