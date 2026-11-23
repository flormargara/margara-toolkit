"""Tests de los chequeos de domains/collections/checks."""

from __future__ import annotations

import random
import unittest

from _util import CheckTest, run, script

CONTROL = script("collections", "check_control_group.py")
TRAINING = script("collections", "check_training_population.py")

SHARES = {"A": 0.03, "B": 0.05, "C": 0.08}
EXPECTED = ["--expected", "A=0.03,B=0.05,C=0.08"]


class ControlGroupTest(CheckTest):
    HEADER = ["id", "fecha_corrida", "rating", "grupo", "pase"]

    def assignments(self, shares=SHARES, switch: int = 0, runs: int = 6, units: int = 6000):
        """Control persistente asignado una vez por cuenta; switch cuentas cambian en la última corrida."""
        rng = random.Random(5)
        group, rows = {}, []
        for run_no in range(runs):
            for a in range(units):
                rating = "ABC"[a % 3]
                group.setdefault(a, "control" if rng.random() < shares[rating] else "tratamiento")
                g = group[a]
                if run_no == runs - 1 and a < switch:
                    g = "control" if g == "tratamiento" else "tratamiento"
                rows.append([a, f"2026-{run_no + 1:02d}-01", rating, g, int(rng.random() < 0.2)])
        return self.csv("asig.csv", self.HEADER, rows)

    def test_control_sano(self):
        self.assertPasses(run(CONTROL, self.assignments(), *EXPECTED))

    def test_cuenta_que_cambia_de_grupo(self):
        self.assertFails(run(CONTROL, self.assignments(switch=3), *EXPECTED),
                         "persistencia: 3 de 6000 unidades cambiaron de grupo")

    def test_proporcion_fuera_de_lo_esperado(self):
        self.assertFails(run(CONTROL, self.assignments(shares=dict(SHARES, C=0.15)), *EXPECTED),
                         "FAIL  proporción C")

    def test_proporcion_contada_por_cuenta(self):
        # Con muchas corridas por cuenta, contar filas achicaría el desvío y fallaría por ruido.
        self.assertPasses(run(CONTROL, self.assignments(runs=12), *EXPECTED))

    def test_proporcion_unica_para_todos_los_ratings(self):
        path = self.assignments(shares={"A": 0.05, "B": 0.05, "C": 0.05})
        self.assertPasses(run(CONTROL, path, "--expected", "0.05"))

    def test_control_insuficiente_para_reentrenar(self):
        r = run(CONTROL, self.assignments(), *EXPECTED, "--target-col", "pase", "--min-control-events", 100000)
        self.assertFails(r, "mínimo 100000 para reentrenar")

    def test_rating_sin_proporcion_esperada(self):
        self.assertFails(run(CONTROL, self.assignments(), "--expected", "A=0.03,B=0.05"),
                         "rating C sin proporción esperada")

    def test_grupo_desconocido(self):
        path = self.csv("asig.csv", self.HEADER, [[1, "2026-01-01", "A", "otro", 0],
                                                  [2, "2026-01-01", "A", "control", 0]])
        self.assertFails(run(CONTROL, path, "--expected", "0.5"), "grupo vacío o desconocido: 1")

    def test_fechas_en_otro_formato(self):
        # El orden de las corridas sale de la fecha, no del texto.
        rows = [[1, "15/01/2026", "A", "tratamiento", 0], [1, "01/02/2026", "A", "control", 0]]
        r = run(CONTROL, self.csv("asig.csv", self.HEADER, rows), "--expected", "0.5")
        self.assertIn("tratamiento 15/01/2026 → control 01/02/2026", r.stdout)


class TrainingPopulationTest(CheckTest):
    HEADER = ["id", "fecha_corte", "grupo", "split"]
    START = ["--model-start", "2026-03-01"]

    def universe(self, treated_after_start: bool = False, pre_group: str = "sin_gestion", empty_after: bool = False):
        rows = []
        for i in range(600):
            month = i % 6 + 1
            if month < 3:
                g = pre_group
            elif empty_after and i == 302:  # mes 3, después del inicio del modelo
                g = ""
            elif treated_after_start and i % 2:
                g = "tratamiento"
            else:
                g = "control"
            rows.append([i, f"2026-{month:02d}-15", g, "train" if i < 500 else "val"])
        rows += [[1000 + i, "2026-07-15", "tratamiento", "score"] for i in range(50)]
        return self.csv("u.csv", self.HEADER, rows)

    def test_solo_control_desde_el_modelo(self):
        r = run(TRAINING, self.universe(), *self.START, "--split-col", "split")
        self.assertPasses(r)
        self.assertIn("documentar qué gestión recibieron", r.stdout)

    def test_filas_tratadas_desde_el_modelo(self):
        r = run(TRAINING, self.universe(treated_after_start=True), *self.START, "--split-col", "split")
        self.assertFails(r, "FAIL  train:", "FAIL  val:")

    def test_filas_de_scoring_no_se_evaluan(self):
        r = run(TRAINING, self.universe(), *self.START, "--split-col", "split")
        self.assertNotIn("score", r.stdout.split("partición")[1].split("\n\n")[0])

    def test_grupo_vacio_desde_el_modelo(self):
        r = run(TRAINING, self.universe(empty_after=True), *self.START, "--split-col", "split")
        self.assertFails(r, "filas sin grupo")

    def test_autocura_exige_sin_gestion_en_toda_fecha(self):
        path = self.universe(pre_group="gestion_habitual")
        self.assertPasses(run(TRAINING, path, *self.START, "--split-col", "split"))
        self.assertFails(run(TRAINING, path, *self.START, "--split-col", "split", "--target-kind", "autocura"),
                         "gestionadas en un target de autocura")
        self.assertPasses(run(TRAINING, self.universe(), *self.START, "--split-col", "split",
                              "--target-kind", "autocura"))


if __name__ == "__main__":
    unittest.main()
