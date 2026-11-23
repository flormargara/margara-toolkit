#!/usr/bin/env python3
"""Validación de una escala de ratings contra el target observado.

Entrada: un CSV con una fila por entidad puntuada, con la columna de rating y la de
target binario (1 = malo). Las filas con target vacío (inmaduras o indeterminadas) se
cuentan y se excluyen. Se corre en la muestra donde se verifican los cortes (OOT),
no en la que se calcularon.

Uso:
  check_ratings.py oot.csv --order A,B,C,D,E --expected A=0.01,B=0.03,C=0.06,D=0.12,E=0.25
  check_ratings.py oot.csv --order A,B,C,D,E --expected-file perfil.csv --score-col score \
      --cohort-col cohorte --residual AA,F
  check_ratings.py cobranzas.csv --order 1,2,3,4 --where grupo=control

Chequeos (FAIL hace salir con 1):
  1. Monotonía: la tasa de malos sube de forma estricta de la mejor a la peor banda.  FAIL
  2. Tamaño mínimo: cada banda (salvo las residuales) tiene al menos --min-share
     de la población.                                                             FAIL
  3. Calibración: |tasa observada − esperada| <= --tolerance en cada banda con tasa
     esperada (si se pasa --expected o --expected-file).                           FAIL
  4. Cortes deterministas: los rangos de score de las bandas no se superponen y
     avanzan en un solo sentido (si se pasa --score-col).                          FAIL
  5. Malos suficientes: al menos --min-bads malos por banda.                       WARN
  6. Separación: bandas contiguas con tasas que no difieren significativamente
     (prueba de dos proporciones, |z| < 1.96) podrían unirse.                      WARN
  7. Estabilidad: con --cohort-col, monotonía y calibración en cada cohorte con
     malos suficientes.                                                           WARN

Con --where columna=valor (repetible) se filtra antes de evaluar: en cobranzas, o
cuando la acción cambia el resultado, evaluar sobre el grupo de control.

Salida: 0 si todo pasa; 1 si algún chequeo falla. Solo biblioteca estándar.
"""

from __future__ import annotations

import argparse
import csv
import math
import sys
from collections import defaultdict

NULLS = {"", "na", "nan", "null", "none"}


def parse_map(text: str | None, flag: str) -> dict[str, float]:
    out: dict[str, float] = {}
    for part in (text or "").split(","):
        if not part.strip():
            continue
        if "=" not in part:
            raise SystemExit(f"{flag} espera banda=valor, recibió {part!r}")
        k, v = part.split("=", 1)
        out[k.strip()] = float(v)
    return out


def read_expected_file(path: str) -> dict[str, float]:
    with open(path, newline="", encoding="utf-8") as fh:
        reader = csv.reader(fh)
        rows = [r for r in reader if r]
    if rows and not _is_number(rows[0][1]):
        rows = rows[1:]
    return {r[0].strip(): float(r[1]) for r in rows}


def _is_number(text: str) -> bool:
    try:
        float(text)
        return True
    except ValueError:
        return False


def parse_target(value: str) -> int | None:
    v = (value or "").strip().lower()
    if v in NULLS:
        return None
    if v in {"1", "1.0", "true", "si", "sí", "malo", "bad"}:
        return 1
    if v in {"0", "0.0", "false", "no", "bueno", "good"}:
        return 0
    raise SystemExit(f"target no binario: {value!r}")


def two_prop_z(b1: int, n1: int, b2: int, n2: int) -> float:
    if not n1 or not n2:
        return 0.0
    p = (b1 + b2) / (n1 + n2)
    se = math.sqrt(p * (1 - p) * (1 / n1 + 1 / n2))
    return 0.0 if se == 0 else (b2 / n2 - b1 / n1) / se


def wilson(b: int, n: int, z: float = 1.96) -> tuple[float, float]:
    if not n:
        return (0.0, 0.0)
    p = b / n
    den = 1 + z * z / n
    c = (p + z * z / (2 * n)) / den
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return (max(0.0, c - h), min(1.0, c + h))


def evaluate(stats, order, expected, tol, min_bads, label, results, level_fail):
    """Monotonía, calibración y malos suficientes para un grupo de filas."""
    present = [r for r in order if stats[r][0]]
    rates = {r: stats[r][1] / stats[r][0] for r in present}
    for a, b in zip(present, present[1:]):
        ok = rates[b] > rates[a]
        results.append((
            "OK" if ok else level_fail, label,
            f"monotonía {a} → {b}: {rates[a]:.2%} {'<' if ok else '>='} {rates[b]:.2%}",
        ))
    for r in present:
        if r in expected:
            diff = rates[r] - expected[r]
            ok = abs(diff) <= tol
            results.append((
                "OK" if ok else level_fail, label,
                f"calibración {r}: observada {rates[r]:.2%} vs esperada {expected[r]:.2%} "
                f"(dif {diff:+.2%}, tolerancia ±{tol:.2%})",
            ))
    if min_bads and level_fail == "FAIL":
        for r in present:
            if stats[r][1] < min_bads:
                results.append(("WARN", label, f"malos en {r}: {stats[r][1]} < {min_bads}; tasa inestable"))


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("data")
    p.add_argument("--rating-col", default="rating")
    p.add_argument("--target-col", default="target")
    p.add_argument("--order", help="Bandas de la mejor a la peor, separadas por coma "
                                   "(por defecto, orden alfabético o numérico ascendente)")
    p.add_argument("--expected", help="Tasa esperada por banda: A=0.01,B=0.03")
    p.add_argument("--expected-file", help="CSV banda,tasa_esperada")
    p.add_argument("--tolerance", type=float, default=0.05, help="Máxima diferencia absoluta (0.05 = 5 puntos)")
    p.add_argument("--min-share", type=float, default=0.03)
    p.add_argument("--min-bads", type=int, default=30)
    p.add_argument("--residual", default="", help="Bandas residuales de los extremos, exentas de --min-share")
    p.add_argument("--score-col", help="Score continuo, para verificar que los cortes no se superponen")
    p.add_argument("--cohort-col", help="Cohorte (por ejemplo, mes de originación) para estabilidad")
    p.add_argument("--where", action="append", default=[], help="Filtro columna=valor (repetible)")
    args = p.parse_args()

    filters = []
    for w in args.where:
        if "=" not in w:
            raise SystemExit(f"--where espera columna=valor, recibió {w!r}")
        c, v = w.split("=", 1)
        filters.append((c.strip(), v.strip()))

    expected = parse_map(args.expected, "--expected")
    if args.expected_file:
        expected.update(read_expected_file(args.expected_file))
    residual = {r.strip() for r in args.residual.split(",") if r.strip()}

    stats = defaultdict(lambda: [0, 0])          # rating -> [n, malos]
    cohort_stats = defaultdict(lambda: defaultdict(lambda: [0, 0]))
    score_range: dict[str, list[float]] = {}
    total_rows = filtered_out = no_target = 0

    with open(args.data, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        cols = reader.fieldnames or []
        needed = [args.rating_col, args.target_col, args.score_col, args.cohort_col] + [c for c, _ in filters]
        missing = [c for c in needed if c and c not in cols]
        if missing:
            raise SystemExit(f"columnas ausentes en {args.data}: {', '.join(missing)}")
        for row in reader:
            total_rows += 1
            if any(row[c].strip() != v for c, v in filters):
                filtered_out += 1
                continue
            t = parse_target(row[args.target_col])
            if t is None:
                no_target += 1
                continue
            r = row[args.rating_col].strip()
            stats[r][0] += 1
            stats[r][1] += t
            if args.cohort_col:
                cs = cohort_stats[row[args.cohort_col].strip()][r]
                cs[0] += 1
                cs[1] += t
            if args.score_col and row[args.score_col].strip().lower() not in NULLS:
                s = float(row[args.score_col])
                rng = score_range.setdefault(r, [s, s])
                rng[0], rng[1] = min(rng[0], s), max(rng[1], s)

    n_total = sum(v[0] for v in stats.values())
    if not n_total:
        print("no quedan filas con target después de filtrar", file=sys.stderr)
        return 1

    if args.order:
        order = [r.strip() for r in args.order.split(",") if r.strip()]
    else:
        labels = list(stats)
        order = sorted(labels, key=float) if all(_is_number(x) for x in labels) else sorted(labels)
    unknown = sorted(set(stats) - set(order))

    results: list[tuple[str, str, str]] = []
    if not args.order:
        results.append(("WARN", "", f"sin --order: se asume {','.join(order)} de la mejor a la peor banda"))
    if unknown:
        results.append(("FAIL", "", f"bandas fuera de --order: {', '.join(unknown)}"))
    for r in expected:
        if r not in order:
            results.append(("WARN", "", f"banda con tasa esperada que no está en --order: {r}"))

    print(f"Filas: {total_rows}; filtradas por --where: {filtered_out}; sin target: {no_target}; evaluadas: {n_total}\n")
    print(f"{'banda':<8}{'n':>9}{'part.':>8}{'malos':>8}{'tasa':>9}{'IC 95%':>18}{'esperada':>10}{'dif':>9}")
    for r in order:
        n, b = stats[r]
        if not n:
            print(f"{r:<8}{0:>9}")
            continue
        lo, hi = wilson(b, n)
        exp = f"{expected[r]:.2%}" if r in expected else "—"
        dif = f"{b / n - expected[r]:+.2%}" if r in expected else "—"
        print(f"{r:<8}{n:>9}{n / n_total:>8.1%}{b:>8}{b / n:>9.2%}{f'{lo:.2%}–{hi:.2%}':>18}{exp:>10}{dif:>9}")
    print()

    for r in order:
        if not stats[r][0]:
            results.append(("WARN", "", f"banda {r} sin filas"))

    evaluate(stats, order, expected, args.tolerance, args.min_bads, "", results, "FAIL")

    for r in order:
        n = stats[r][0]
        if n and r not in residual:
            share = n / n_total
            ok = share >= args.min_share
            results.append((
                "OK" if ok else "FAIL", "",
                f"tamaño {r}: {share:.1%} {'>=' if ok else '<'} {args.min_share:.1%}",
            ))

    present = [r for r in order if stats[r][0]]
    for a, b in zip(present, present[1:]):
        z = two_prop_z(stats[a][1], stats[a][0], stats[b][1], stats[b][0])
        if abs(z) < 1.96:
            results.append(("WARN", "", f"separación {a} / {b}: z = {z:.2f}; las tasas no difieren "
                                        "significativamente, evaluar unirlas"))

    if args.score_col:
        ranged = [r for r in order if r in score_range]
        directions = set()
        for a, b in zip(ranged, ranged[1:]):
            (a_lo, a_hi), (b_lo, b_hi) = score_range[a], score_range[b]
            if a_hi < b_lo:
                directions.add("sube")
            elif b_hi < a_lo:
                directions.add("baja")
            else:
                results.append(("FAIL", "", f"cortes {a} / {b}: rangos de score superpuestos "
                                            f"[{a_lo:g}, {a_hi:g}] y [{b_lo:g}, {b_hi:g}]"))
        if len(directions) > 1:
            results.append(("FAIL", "", "cortes: los rangos de score no avanzan en un solo sentido"))
        elif directions:
            results.append(("OK", "", f"cortes: rangos de score disjuntos; el score {directions.pop()} "
                                      "de la mejor a la peor banda"))

    if args.cohort_col:
        for cohort in sorted(cohort_stats):
            cstats = cohort_stats[cohort]
            if sum(v[1] for v in cstats.values()) < args.min_bads:
                results.append(("WARN", f"[{cohort}] ", "cohorte con pocos malos; no evaluada"))
                continue
            cres: list[tuple[str, str, str]] = []
            evaluate(cstats, order, expected, args.tolerance, 0, f"[{cohort}] ", cres, "WARN")
            bad = [x for x in cres if x[0] == "WARN"]
            results.extend(bad if bad else [("OK", f"[{cohort}] ", "monotonía y calibración estables")])

    for status, label, msg in results:
        print(f"{status:<5} {label}{msg}")
    print("MANUAL verificar los cortes en una muestra distinta de la que los calculó y estresarlos (submuestras)")
    print("MANUAL confirmar que cada banda lleva a una acción distinta")

    failed = any(s == "FAIL" for s, _, _ in results)
    print("\nVeredicto:", "❌ la escala no cumple" if failed else "✅ escala de ratings verificada")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
