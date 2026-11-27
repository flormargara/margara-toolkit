"""Tests de los scripts del propio toolkit (scripts/)."""

from __future__ import annotations

import os
import unittest

from _util import ROOT, CheckTest, run

LINT = ROOT / "scripts" / "lint_skills.py"


class LintSkillsTest(CheckTest):
    def repo(self, skill_md: str | None = None, knowledge: str = "Ver `b.md` y `check_x.py`.\n"):
        skill = self.tmp / "adapters" / "claude" / "skills" / "demo"
        skill.mkdir(parents=True)
        (skill / "SKILL.md").write_text(
            skill_md or "---\nname: demo\ndescription: Demo skill.\n---\nLeer `dom/knowledge/a.md`.\n",
            encoding="utf-8")
        know = self.tmp / "domains" / "dom" / "knowledge"
        know.mkdir(parents=True)
        (know / "a.md").write_text(knowledge, encoding="utf-8")
        (know / "b.md").write_text("ok\n", encoding="utf-8")
        checks = self.tmp / "domains" / "dom" / "checks"
        checks.mkdir()
        (checks / "check_x.py").write_text("print('ok')\n", encoding="utf-8")
        (self.tmp / "shared").mkdir()
        os.symlink("../../../../domains/dom", skill / "dom")
        return skill

    def lint(self):
        return run(LINT, "--root", self.tmp)

    def test_el_repo_real_pasa(self):
        self.assertPasses(run(LINT))

    def test_repo_sano(self):
        self.repo()
        self.assertPasses(self.lint())

    def test_referencia_rota(self):
        self.repo(knowledge="Ver `c.md` y `templates/ficha.md`.\n")
        self.assertFails(self.lint(), "no existe c.md", "no existe templates/ficha.md")

    def test_ignora_archivos_del_proyecto(self):
        self.repo(knowledge="Crear `MODELING_SPEC.md`, `forbidden_columns.txt` y `<proyecto>/x.md`.\n")
        self.assertPasses(self.lint())

    def test_ruta_absoluta(self):
        self.repo(knowledge="Correr /Users/alguien/proyecto/check.py\n")
        self.assertFails(self.lint(), "a.md:1: ruta absoluta")

    def test_frontmatter_y_enlace_roto(self):
        skill = self.repo(skill_md="---\nname: otra\ndescription:\n---\n")
        os.symlink("../no-existe", skill / "roto")
        self.assertFails(self.lint(), "no coincide con la carpeta", "description vacía", "enlace roto")


if __name__ == "__main__":
    unittest.main()
