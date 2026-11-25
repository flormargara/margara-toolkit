"""Tests de los chequeos genéricos de domains/ml-foundations/checks."""

from __future__ import annotations

import json
import random
import unittest

from _util import CheckTest, run, script

TARGET_PROFILE = script("ml-foundations", "target_profile.py")
UNIVERSE = script("ml-foundations", "check_universe.py")
DATASET = script("ml-foundations", "check_dataset.py")
LEAKAGE = script("ml-foundations", "check_leakage.py")
CONCENTRATION = script("ml-foundations", "check_concentration.py")
PSI = script("ml-foundations", "psi.py")
FEATURE_NAMES = script("ml-foundations", "check_feature_names.py")


class TargetProfileTest(CheckTest):
    def rows(self, positives_per_month: dict[int, int], volume: int = 500):
        out = []
        for month, positives in positives_per_month.items():
            for i in range(volume):
                out.append([f"2025-{month:02d}-15", int(i < positives)])
        return out

    def test_estable_es_viable(self):
        path = self.csv("u.csv", ["fecha_corte", "target"], self.rows({m: 50 for m in range(1, 13)}))
        self.assertPasses(run(TARGET_PROFILE, path))

    def test_pocos_eventos_no_es_viable(self):
        path = self.csv("u.csv", ["fecha_corte", "target"], self.rows({m: 3 for m in range(1, 13)}))
        self.assertFails(run(TARGET_PROFILE, path), "descartado")

    def test_salto_de_regimen_es_parcial(self):
        counts = {m: (50 if m <= 6 else 200) for m in range(1, 13)}
        path = self.csv("u.csv", ["fecha_corte", "target"], self.rows(counts))
        self.assertFails(run(TARGET_PROFILE, path), "parcial")


class UniverseTest(CheckTest):
    HEADER = ["id", "fecha_corte", "split"]

    def universe(self, val_date: str = "2025-10-15", val_ids=range(100, 110)):
        rows = [[i, f"2025-0{m}-15", "train"] for i in range(10) for m in range(1, 7)]
        rows += [[i, val_date, "val"] for i in val_ids]
        return self.csv("u.csv", self.HEADER, rows)

    def test_universo_sano(self):
        r = run(UNIVERSE, self.universe(), "--horizon-days", 30, "--last-data-date", "2026-03-31",
                "--order", "train,val", "--id-col", "id")
        self.assertPasses(r)

    def test_horizonte_superpuesto(self):
        r = run(UNIVERSE, self.universe(val_date="2025-07-01"), "--horizon-days", 30,
                "--last-data-date", "2026-03-31", "--order", "train,val", "--id-col", "id")
        self.assertFails(r, "FAIL", "horizonte train → val")

    def test_cohorte_inmadura(self):
        r = run(UNIVERSE, self.universe(), "--horizon-days", 30, "--last-data-date", "2025-10-31",
                "--order", "train,val", "--id-col", "id")
        self.assertFails(r, "horizonte completo: 10 filas")

    def test_entidades_compartidas(self):
        path = self.universe(val_ids=range(5, 15))
        args = ["--horizon-days", 30, "--last-data-date", "2026-03-31", "--order", "train,val", "--id-col", "id"]
        self.assertFails(run(UNIVERSE, path, *args), "entidades compartidas train / val: 5")
        # Con --arbiter-overlap, compartir entidades con la validación final es advertencia.
        self.assertPasses(run(UNIVERSE, path, *args, "--arbiter-overlap"))


class DatasetTest(CheckTest):
    def build(self, train_extra=None, val_header=None, universe_bads=5):
        header = ["id", "fecha_corte", "f1", "target"]
        train = [[i, "2025-03-31", i * 1.5, int(i < 5)] for i in range(50)] + (train_extra or [])
        val = [[i, "2025-09-30", i * 1.5, int(i < 3)] for i in range(100, 130)]
        score = [[i, "2025-12-31", i * 1.5] for i in range(200, 220)]
        u_train = [[i, "2025-03-31", int(i < universe_bads)] for i in range(50)]
        return [
            "--split", f"train={self.csv('m_train.csv', header, train)}",
            "--split", f"val={self.csv('m_val.csv', val_header or header, val)}",
            "--split", f"score={self.csv('m_score.csv', header[:3], score)}",
            "--universe", f"train={self.csv('u_train.csv', ['id', 'fecha_corte', 'target'], u_train)}",
            "--id-col", "id",
        ]

    def test_dataset_sano(self):
        self.assertPasses(run(DATASET, *self.build()))

    def test_duplicado_de_grano(self):
        self.assertFails(run(DATASET, *self.build(train_extra=[[0, "2025-03-31", 0.0, 1]])), "FAIL")

    def test_target_no_preservado(self):
        self.assertFails(run(DATASET, *self.build(universe_bads=7)), "FAIL")

    def test_esquema_distinto(self):
        self.assertFails(run(DATASET, *self.build(val_header=["id", "fecha_corte", "f2", "target"])), "FAIL")


class LeakageTest(CheckTest):
    def setUp(self):
        super().setUp()
        self.patterns = self.text("patterns.txt", "# prueba\n\\w*_futur[oa]s?\\b\n\\bdias_atraso_actual\\b\n")

    def test_lista_limpia(self):
        features = self.text("features.txt", "edad\ningreso\n")
        self.assertPasses(run(LEAKAGE, "--features", features, "--patterns", self.patterns))

    def test_feature_prohibida(self):
        features = self.text("features.txt", "edad\npagos_futuros\n")
        self.assertFails(run(LEAKAGE, "--features", features, "--patterns", self.patterns), "pagos_futuros")

    def test_codigo_con_marca_permitida(self):
        code = self.text("fe.py", "y = df['dias_atraso_actual'] > 90  # leakage-ok: construye el target\n")
        self.assertPasses(run(LEAKAGE, code, "--patterns", self.patterns))
        code.write_text("X['d'] = df['dias_atraso_actual']\n", encoding="utf-8")
        self.assertFails(run(LEAKAGE, code, "--patterns", self.patterns), "dias_atraso_actual")

    def test_notebook(self):
        nb = {"cells": [{"cell_type": "code", "source": ["a = 1\n", "b = df.pago_futuro\n"]}]}
        path = self.text("fe.ipynb", json.dumps(nb))
        self.assertFails(run(LEAKAGE, path, "--patterns", self.patterns), "celda 1, línea 2")

    def test_modo_hook_sale_con_2(self):
        code = self.text("fe.py", "x = df.pago_futuro\n")
        (self.tmp / "forbidden_columns.txt").write_text(self.patterns.read_text(), encoding="utf-8")
        payload = json.dumps({"tool_input": {"file_path": str(code)}, "cwd": str(self.tmp)})
        self.assertFails(run(LEAKAGE, "--hook", stdin=payload, cwd=self.tmp), "pago_futuro", code=2)
        # Un archivo fuera de --include no se escanea.
        self.assertPasses(run(LEAKAGE, "--hook", "--include", "src/**", stdin=payload, cwd=self.tmp))


class ConcentrationTest(CheckTest):
    def test_importancia_repartida(self):
        path = self.csv("imp.csv", ["feature", "importance"], [[f"f{i}", 1.0] for i in range(10)])
        self.assertPasses(run(CONCENTRATION, path))

    def test_una_variable_domina(self):
        rows = [["f0", 50.0]] + [[f"f{i}", 1.0] for i in range(1, 10)]
        self.assertFails(run(CONCENTRATION, self.csv("imp.csv", ["feature", "importance"], rows)))

    def test_json(self):
        path = self.text("imp.json", json.dumps({f"f{i}": 1.0 for i in range(10)}))
        self.assertPasses(run(CONCENTRATION, path))


class PsiTest(CheckTest):
    def sample(self, name: str, shift: float):
        rng = random.Random(7)
        return self.csv(name, ["score", "edad"], [[rng.random() + shift, rng.randint(18, 80)] for _ in range(2000)])

    def test_misma_distribucion(self):
        r = run(PSI, self.sample("ref.csv", 0), self.sample("act.csv", 0), "--column", "score", "--fail-above", 0.1)
        self.assertPasses(r)
        self.assertIn("estable", r.stdout)

    def test_distribucion_corrida(self):
        r = run(PSI, self.sample("ref.csv", 0), self.sample("act.csv", 0.5), "--column", "score", "--fail-above", 0.25)
        self.assertFails(r, "significativo")

    def test_csi_todas_las_numericas(self):
        r = run(PSI, self.sample("ref.csv", 0), self.sample("act.csv", 0), "--all-numeric")
        self.assertPasses(r)
        self.assertIn("score:", r.stdout)
        self.assertIn("edad:", r.stdout)

    def test_columna_ausente(self):
        r = run(PSI, self.sample("ref.csv", 0), self.sample("act.csv", 0), "--column", "otra")
        self.assertFails(r, "no está en ambos archivos", code=2)


class FeatureNamesTest(CheckTest):
    VALID = "BUR_TAR_CNT_CONSULTAS_6M\nAPP_PRE_FLG_MORAMAYOR30_NO\nAPP_TAR_CAT_TIPOTARJETA_1M\n"

    def test_nombres_validos_y_tipos(self):
        out = self.tmp / "tipos.csv"
        r = run(FEATURE_NAMES, self.text("f.txt", self.VALID), "--types-out", out)
        self.assertPasses(r)
        self.assertIn("1 numéricas, 1 categóricas, 1 banderas", r.stdout)
        self.assertIn("APP_TAR_CAT_TIPOTARJETA_1M,categórica", out.read_text(encoding="utf-8"))

    def test_tipo_por_segmento_no_por_substring(self):
        # CAT dentro de la descripción no la vuelve categórica.
        out = self.tmp / "tipos.csv"
        r = run(FEATURE_NAMES, self.text("f.txt", "APP_TAR_CNT_CATALOGO_3M\n"), "--types-out", out)
        self.assertPasses(r)
        self.assertIn("APP_TAR_CNT_CATALOGO_3M,numérica", out.read_text(encoding="utf-8"))

    def test_encabezado_de_csv_ignorando_claves(self):
        path = self.csv("d.csv", ["id", "fecha_corte", "BUR_TAR_CNT_CONSULTAS_6M", "target"], [[1, "2025-01-31", 3, 0]])
        self.assertPasses(run(FEATURE_NAMES, path, "--ignore", "id,fecha_corte,target"))

    def test_formato_invalido(self):
        names = "bur_tar_cnt_consultas_6m\nBUR_TAR_CONSULTAS_6M\nBUR_TAR_XYZ_CONSULTAS_6M\nBUR_TAR_CNT_CONSULTAS_HIST\nBUR_TAR_CNT_CONSULTAS_6M\nBUR_TAR_CNT_CONSULTAS_6M\n"
        r = run(FEATURE_NAMES, self.text("f.txt", names))
        self.assertFails(r, "mayúsculas", "4 segmentos", "'XYZ' no está en el catálogo", "'HIST' no es una ventana", "repetido")

    def test_listas_del_proyecto_y_operaciones_extra(self):
        path = self.text("f.txt", "BUR_TAR_RSI_CONSULTAS_6M\n")
        self.assertFails(run(FEATURE_NAMES, path, "--extra-ops", "RSI", "--sources", "APP"), "fuente 'BUR' no está en la lista")
        self.assertPasses(run(FEATURE_NAMES, path, "--extra-ops", "RSI", "--sources", "APP,BUR", "--domains", "TAR"))


if __name__ == "__main__":
    unittest.main()
