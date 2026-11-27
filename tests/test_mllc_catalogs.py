"""Tests de los catálogos de golden rules de adapters/mllc.

Verifican que los catálogos tengan el formato que acepta ai-mllc (vía compose.py) y que
cada comando que una regla pide correr use un chequeo y flags que existen. Así, si un
chequeo cambia de interfaz, el catálogo que lo nombra falla acá y no en un proyecto.
"""

from __future__ import annotations

import re
import unittest

from _util import DOMAINS, ROOT, CheckTest, run

COMPOSE = ROOT / "adapters" / "mllc" / "compose.py"
CATALOGS = ROOT / "adapters" / "mllc" / "golden-rules"
COMMAND = re.compile(r"`python3 (\S+\.py)([^`]*)`")


def find_check(name: str):
    matches = sorted(DOMAINS.glob(f"*/checks/{name}"))
    return matches[0] if matches else None


class CatalogsTest(CheckTest):
    def test_todos_los_catalogos_son_validos(self):
        self.assertPasses(run(COMPOSE, "--check"))

    def test_se_componen_en_orden_sin_ids_repetidos(self):
        r = run(COMPOSE, "ml-foundations", "credit-scoring", "collections", "--out", "-")
        self.assertPasses(r)
        ids = re.findall(r"^## (\S+) \(v\d+\)", r.stdout, re.M)
        self.assertEqual(len(ids), len(set(ids)))
        self.assertTrue(any(i.startswith("cr-") for i in ids))
        self.assertTrue(any(i.startswith("co-") for i in ids))

    def test_al_componer_los_chequeos_quedan_con_ruta_completa(self):
        r = run(COMPOSE, "ml-foundations", "credit-scoring", "collections", "--out", "-")
        self.assertPasses(r)
        commands = re.findall(r"python3 (\S+\.py)", r.stdout)
        self.assertTrue(commands)
        for command in commands:
            self.assertIn("/checks/", command)

    def test_los_comandos_de_las_reglas_existen(self):
        for catalog in sorted(CATALOGS.glob("*.md")):
            for script, args in COMMAND.findall(catalog.read_text(encoding="utf-8")):
                with self.subTest(catalog=catalog.name, script=script):
                    path = find_check(script)
                    self.assertIsNotNone(path, f"{catalog.name} nombra {script}, que no existe")
                    helptext = run(path, "--help").stdout
                    for flag in set(re.findall(r"--[a-z][a-z-]*", args)):
                        self.assertIn(flag, helptext, f"{catalog.name}: {script} no tiene {flag}")


if __name__ == "__main__":
    unittest.main()
