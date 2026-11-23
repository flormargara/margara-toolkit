"""Tests de los chequeos de domains/credit-scoring/checks."""

from __future__ import annotations

import random
import unittest

from _util import CheckTest, run, script

RATINGS = script("credit-scoring", "check_ratings.py")
WOE = script("credit-scoring", "check_woe_bins.py")
ROLL = script("credit-scoring", "roll_rate.py")

EXPECTED = {"A": 0.01, "B": 0.03, "C": 0.07, "D": 0.15, "E": 0.30}
SCORE_RANGES = {"A": (800, 900), "B": (700, 799), "C": (600, 699), "D": (500, 599), "E": (300, 499)}


def rated_rows(rates: dict[str, float], n: int = 3000, overlap: bool = False):
    """Filas id, score, rating, target, cohorte, grupo con tasas exactas por banda."""
    rng = random.Random(3)
    rows, i = [], 0
    for rating, rate in rates.items():
        bads = round(n * rate)
        lo, hi = (0, 1000) if overlap else SCORE_RANGES[rating]
        for k in range(n):
            i += 1
            rows.append([i, rng.randint(lo, hi), rating, int(k % (n // bads or 1) == 0 and k // (n // bads) < bads),
                         "2026-01" if k % 2 else "2026-02", "control" if k % 3 else "tratamiento"])
    return rows


class RatingsTest(CheckTest):
    HEADER = ["id", "score", "rating", "target", "cohorte", "grupo"]
    ORDER = ["--order", "A,B,C,D,E"]
    EXP = ["--expected", ",".join(f"{k}={v}" for k, v in EXPECTED.items())]

    def test_escala_sana(self):
        path = self.csv("oot.csv", self.HEADER, rated_rows(EXPECTED))
        r = run(RATINGS, path, *self.ORDER, *self.EXP, "--score-col", "score", "--cohort-col", "cohorte")
        self.assertPasses(r)
        self.assertIn("✅", r.stdout)

    def test_no_monotona(self):
        rates = dict(EXPECTED, C=0.02)
        r = run(RATINGS, self.csv("oot.csv", self.HEADER, rated_rows(rates)), *self.ORDER)
        self.assertFails(r, "FAIL  monotonía B → C")

    def test_fuera_de_tolerancia(self):
        rates = dict(EXPECTED, E=0.45)
        r = run(RATINGS, self.csv("oot.csv", self.HEADER, rated_rows(rates)), *self.ORDER, *self.EXP)
        self.assertFails(r, "FAIL  calibración E")

    def test_banda_chica(self):
        rows = [r for r in rated_rows(EXPECTED) if r[2] != "E" or r[0] % 50 == 0]
        r = run(RATINGS, self.csv("oot.csv", self.HEADER, rows), *self.ORDER, "--min-bads", 0)
        self.assertFails(r, "FAIL  tamaño E")
        # Si E es una banda residual, el tamaño no se exige.
        self.assertNotIn("tamaño E", run(RATINGS, self.csv("oot2.csv", self.HEADER, rows), *self.ORDER,
                                         "--residual", "E").stdout)

    def test_cortes_superpuestos(self):
        path = self.csv("oot.csv", self.HEADER, rated_rows(EXPECTED, overlap=True))
        self.assertFails(run(RATINGS, path, *self.ORDER, "--score-col", "score"), "rangos de score superpuestos")

    def test_bandas_que_podrian_unirse(self):
        rates = dict(EXPECTED, C=0.031)
        r = run(RATINGS, self.csv("oot.csv", self.HEADER, rated_rows(rates)), *self.ORDER)
        self.assertIn("WARN  separación B / C", r.stdout)

    def test_banda_desconocida(self):
        r = run(RATINGS, self.csv("oot.csv", self.HEADER, rated_rows(EXPECTED)), "--order", "A,B,C,D")
        self.assertFails(r, "bandas fuera de --order: E")

    def test_filtro_where(self):
        path = self.csv("oot.csv", self.HEADER, rated_rows(EXPECTED))
        r = run(RATINGS, path, *self.ORDER, "--where", "grupo=control")
        self.assertIn("filtradas por --where: 5000", r.stdout)


class WoeBinsTest(CheckTest):
    HEADER = ["variable", "bin", "n", "bads"]
    GOOD = [
        ["ingreso", "missing", 600, 60],
        ["ingreso", "[0,500)", 2000, 300],
        ["ingreso", "[500,1000)", 3000, 250],
        ["ingreso", "[1000,inf)", 4400, 200],
    ]

    def test_binning_sano(self):
        self.assertPasses(run(WOE, self.csv("b.csv", self.HEADER, self.GOOD)))

    def test_no_monotono_y_excepcion(self):
        rows = [["edad", "[18,25)", 2000, 200], ["edad", "[25,40)", 4000, 150],
                ["edad", "[40,60)", 3000, 300], ["edad", "[60,inf)", 1000, 60]]
        path = self.csv("b.csv", self.HEADER, rows)
        self.assertFails(run(WOE, path), "WoE no monótono")
        self.assertPasses(run(WOE, path, "--allow-nonmonotonic", "edad"))

    def test_iv_sospechoso(self):
        rows = [["atraso", "0", 8000, 100], ["atraso", "1-30", 1500, 400], ["atraso", "30+", 500, 450]]
        path = self.csv("b.csv", self.HEADER, rows)
        self.assertFails(run(WOE, path), "revisar leakage")
        self.assertPasses(run(WOE, path, "--allow-high-iv", "atraso"))

    def test_bin_sin_malos(self):
        rows = [["x", "a", 1000, 0], ["x", "b", 9000, 500]]
        self.assertFails(run(WOE, self.csv("b.csv", self.HEADER, rows)), "WoE infinito")

    def test_bin_chico_y_bin_especial_chico(self):
        rows = [["x", "missing", 100, 40], ["x", "a", 300, 40], ["x", "b", 4600, 300], ["x", "c", 5000, 200]]
        r = run(WOE, self.csv("b.csv", self.HEADER, rows))
        self.assertFails(r, "FAIL  [x] bin 'a'")
        self.assertIn("WARN  [x] bin 'missing'", r.stdout)

    def test_columnas_de_buenos_y_malos(self):
        rows = [[v, b, n - bads, bads] for v, b, n, bads in self.GOOD]
        path = self.csv("b.csv", ["variable", "bin", "goods", "bads"], rows)
        self.assertPasses(run(WOE, path, "--goods-col", "goods"))


class RollRateTest(CheckTest):
    # Cadena de Markov mensual entre tramos 0, 1-30, 31-60, 61-90, 91+ (absorbente).
    P = {0: [.93, .07, 0, 0, 0], 1: [.55, .25, .20, 0, 0], 2: [.25, .15, .20, .40, 0],
         3: [.08, .04, .08, .20, .60], 4: [0, 0, 0, 0, 1]}
    DPD = {0: 0, 1: 15, 2: 45, 3: 75, 4: 120}

    def setUp(self):
        super().setUp()
        rng = random.Random(1)
        rows = []
        for account in range(2000):
            state = 0
            for m in range(36):
                rows.append([account, f"{2024 + m // 12}-{m % 12 + 1:02d}", self.DPD[state]])
                state = rng.choices(range(5), self.P[state])[0]
        self.history = self.csv("h.csv", ["cuenta", "mes", "dias_atraso"], rows)
        self.args = [self.history, "--id-col", "cuenta", "--period-col", "mes", "--dpd-col", "dias_atraso",
                     "--step", 3]

    def test_definicion_consistente(self):
        r = run(ROLL, *self.args, "--bad-from", "61-90")
        self.assertPasses(r)
        self.assertIn("Punto de no retorno (enfoque 2): 61-90", r.stdout)
        self.assertIn("✅", r.stdout)

    def test_tramo_indeterminado_requiere_revision(self):
        r = run(ROLL, *self.args, "--bad-from", "31-60")
        self.assertPasses(r)
        self.assertIn("31-60 sale indeterminado", r.stdout)
        self.assertIn("⚠️ requiere revisión", r.stdout)

    def test_tramo_bueno_falla(self):
        r = run(ROLL, *self.args, "--bad-from", "1-30")
        self.assertFails(r, "1-30 sale bueno")

    def test_tramos_ya_asignados(self):
        labels = {0: "al dia", 15: "1-30", 45: "31-60", 75: "61-90", 120: "90+"}
        rows = [line.split(",") for line in self.history.read_text().splitlines()[1:]]
        path = self.csv("t.csv", ["cuenta", "mes", "tramo"], [[a, m, labels[int(d)]] for a, m, d in rows])
        r = run(ROLL, path, "--id-col", "cuenta", "--period-col", "mes", "--bucket-col", "tramo",
                "--order", "al dia,1-30,31-60,61-90,90+", "--step", 3, "--bad-from", "61-90")
        self.assertPasses(r)

    def test_sin_ventana_completa(self):
        r = run(ROLL, *self.args, "--perf-months", 40)
        self.assertFails(r, "ventana completa")


if __name__ == "__main__":
    unittest.main()
