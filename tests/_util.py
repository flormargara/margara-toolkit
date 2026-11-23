"""Utilidades comunes de los tests: correr un chequeo como lo correría un usuario y
escribir CSV temporales.

Los tests prueban el contrato de cada chequeo desde afuera: con datos sanos sale con
0 y con datos que violan la regla sale con error y nombra el problema.
"""

from __future__ import annotations

import csv
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOMAINS = ROOT / "domains"


def script(domain: str, name: str) -> Path:
    return DOMAINS / domain / "checks" / name


def run(path: Path, *args: str, stdin: str | None = None, cwd: Path | None = None,
        env: dict | None = None) -> subprocess.CompletedProcess:
    full_env = {k: v for k, v in os.environ.items() if k != "CLAUDE_PROJECT_DIR"}
    full_env.update(env or {})
    return subprocess.run(
        [sys.executable, str(path), *map(str, args)],
        input=stdin, capture_output=True, text=True, cwd=cwd, env=full_env, timeout=60,
    )


class CheckTest(unittest.TestCase):
    """Base con un directorio temporal por test."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def csv(self, name: str, header: list[str], rows) -> Path:
        path = self.tmp / name
        with open(path, "w", newline="", encoding="utf-8") as fh:
            w = csv.writer(fh)
            w.writerow(header)
            w.writerows(rows)
        return path

    def text(self, name: str, content: str) -> Path:
        path = self.tmp / name
        path.write_text(content, encoding="utf-8")
        return path

    def assertPasses(self, result: subprocess.CompletedProcess) -> None:
        self.assertEqual(result.returncode, 0, f"esperaba 0\n{result.stdout}\n{result.stderr}")

    def assertFails(self, result: subprocess.CompletedProcess, *fragments: str, code: int = 1) -> None:
        self.assertEqual(result.returncode, code, f"esperaba {code}\n{result.stdout}\n{result.stderr}")
        out = result.stdout + result.stderr
        for fragment in fragments:
            self.assertIn(fragment, out)
