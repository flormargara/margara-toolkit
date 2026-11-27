#!/usr/bin/env python3
"""Gate de calidad de entradas: pasa / no pasa por tabla, antes de cada corrida.

Compara el estado observado de cada tabla de entrada contra su contrato (ver
knowledge/06-monitoreo.md, "Gate de calidad de entradas"). Si falla, la corrida no
publica predicciones: el código de salida 1 corta el pipeline (falla cerrada).

Entradas:
  --contract  JSON con una entrada por tabla que consume el modelo:
                {"tables": {"cartera.saldos": {
                    "columns": {"id_cliente": "bigint", "saldo": "decimal|double", "fecha": "date"},
                    "critical": true,          # false: sus fallas solo advierten
                    "min_rows": 1000,          # filas mínimas de la última partición
                    "max_drop": 0.30,          # caída máxima contra la partición anterior
                    "max_growth": 1.00,        # crecimiento máximo (opcional, advierte)
                    "max_staleness_days": 2}}} # antigüedad máxima de la última partición
              Un tipo admite alternativas con "|". Los tipos se comparan sin
              parámetros ni mayúsculas: varchar(20) = VARCHAR.
  --schema    CSV table,column,type: lo que hoy tiene cada tabla (por ejemplo, un
              export de information_schema.columns).
  --volumes   CSV table,partition,rows: filas por partición (fecha ISO), de un
              SELECT partición, COUNT(*) ... GROUP BY 1 de las últimas particiones.

Chequeos por tabla:
  1. La tabla existe en el esquema.                                         FAIL
  2. Están todas las columnas esperadas, con su tipo.                       FAIL
     Columnas que el contrato no conoce.                                    WARN
  3. Volumen: la última partición tiene al menos --min_rows filas y no cae
     más de max_drop respecto de la anterior.                               FAIL
     Crece más de max_growth.                                               WARN
  4. Frescura: la última partición no es más vieja que max_staleness_days
     respecto de --run-date.                                                FAIL
En una tabla con "critical": false, los FAIL se informan como WARN.

Uso:
  check_inputs.py --contract contrato.json --schema columnas.csv --volumes volumenes.csv
  check_inputs.py --contract contrato.json --schema columnas.csv --volumes volumenes.csv --run-date 2026-11-27

Salida: 0 si todo pasa; 1 si algún chequeo falla; 2 si una entrada no se puede leer.
Solo biblioteca estándar.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from collections import defaultdict
from datetime import date
from pathlib import Path


def norm_type(t: str) -> str:
    return re.sub(r"\(.*\)", "", t).strip().lower()


def read_csv(path: Path, required: list[str]) -> list[dict]:
    with path.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        missing = [c for c in required if c not in (reader.fieldnames or [])]
        if missing:
            raise KeyError(f"{path.name}: faltan columnas {', '.join(missing)}")
        return list(reader)


def check_table(name: str, spec: dict, schema: dict, volumes: dict, run_date: date) -> list[tuple[str, str]]:
    out = []
    if name not in schema:
        return [("FAIL", "no existe en el esquema observado")]

    # 2. Columnas y tipos
    observed = schema[name]
    expected = spec.get("columns", {})
    missing = [c for c in expected if c not in observed]
    wrong = []
    for col, types in expected.items():
        if col in observed:
            allowed = {norm_type(t) for t in str(types).split("|")}
            if norm_type(observed[col]) not in allowed:
                wrong.append(f"{col} es {observed[col]}, se esperaba {types}")
    extra = [c for c in observed if expected and c not in expected]
    if missing:
        out.append(("FAIL", f"faltan columnas: {', '.join(missing)}"))
    if wrong:
        out.append(("FAIL", "tipos distintos: " + "; ".join(wrong)))
    if extra:
        out.append(("WARN", f"columnas que el contrato no conoce: {', '.join(extra[:10])}"))
    if expected and not (missing or wrong):
        out.append(("OK", f"esquema: {len(expected)} columnas con su tipo"))

    # 3. Volumen y 4. frescura
    parts = sorted(volumes.get(name, {}).items())
    if not parts:
        out.append(("FAIL", "sin particiones en el archivo de volúmenes"))
        return out
    last_date, last_rows = parts[-1]
    min_rows = int(spec.get("min_rows", 1))
    if last_rows < min_rows:
        out.append(("FAIL", f"última partición {last_date}: {last_rows} filas, mínimo {min_rows}"))
    if len(parts) > 1:
        prev_date, prev_rows = parts[-2]
        if prev_rows > 0:
            change = last_rows / prev_rows - 1
            max_drop = float(spec.get("max_drop", 0.30))
            if -change > max_drop:
                out.append(("FAIL", f"volumen cae {-change:.0%} entre {prev_date} y {last_date} (máximo {max_drop:.0%})"))
            elif "max_growth" in spec and change > float(spec["max_growth"]):
                out.append(("WARN", f"volumen crece {change:.0%} entre {prev_date} y {last_date}"))
            elif last_rows >= min_rows:
                out.append(("OK", f"volumen {last_rows} filas ({change:+.0%} contra {prev_date})"))
    elif last_rows >= min_rows:
        out.append(("WARN", f"una sola partición ({last_date}): no se puede comparar el volumen"))

    if "max_staleness_days" in spec:
        age = (run_date - date.fromisoformat(last_date)).days
        limit = int(spec["max_staleness_days"])
        if age > limit:
            out.append(("FAIL", f"última partición {last_date} tiene {age} días (máximo {limit})"))
        else:
            out.append(("OK", f"frescura: última partición {last_date} ({age} días)"))
    return out


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--contract", required=True)
    p.add_argument("--schema", required=True)
    p.add_argument("--volumes", required=True)
    p.add_argument("--run-date", default=date.today().isoformat(), help="Fecha de la corrida (AAAA-MM-DD)")
    args = p.parse_args()

    try:
        contract = json.loads(Path(args.contract).read_text(encoding="utf-8"))["tables"]
        schema: dict[str, dict[str, str]] = defaultdict(dict)
        for r in read_csv(Path(args.schema), ["table", "column", "type"]):
            schema[r["table"]][r["column"]] = r["type"]
        volumes: dict[str, dict[str, int]] = defaultdict(dict)
        for r in read_csv(Path(args.volumes), ["table", "partition", "rows"]):
            volumes[r["table"]][date.fromisoformat(r["partition"].strip()[:10]).isoformat()] = int(float(r["rows"]))
        run_date = date.fromisoformat(args.run_date)
    except (OSError, KeyError, ValueError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2

    failed = False
    for name, spec in contract.items():
        critical = spec.get("critical", True)
        print(f"\n{name}" + ("" if critical else " (no crítica)"))
        for level, msg in check_table(name, spec, schema, volumes, run_date):
            if level == "FAIL" and not critical:
                level = "WARN"
            failed |= level == "FAIL"
            print(f"  {level:<5} {msg}")

    print("\nVEREDICTO: " + ("no pasa: no publicar predicciones" if failed else "pasa"))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
