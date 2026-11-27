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
PROMOTION = script("ml-foundations", "promotion.py")
INPUTS = script("ml-foundations", "check_inputs.py")
TRACEABILITY = script("ml-foundations", "check_traceability.py")


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


class PromotionTest(CheckTest):
    """Cohorte sintética: la probabilidad real sale de una variable latente."""

    def cohort(self, n=3000, seed=7, champion_noise=1.0, champion_scale=1.0,
               challenger_noise=0.2, challenger_scale=1.0, extra=None):
        import math
        rng = random.Random(seed)
        rows = []
        for i in range(n):
            z = rng.gauss(0, 1)
            prob = 1 / (1 + math.exp(-(1.5 * z - 2)))
            y = 1 if rng.random() < prob else 0
            def score(noise, scale):
                return min(0.999, scale / (1 + math.exp(-(1.5 * (z + rng.gauss(0, noise)) - 2))))
            champ = score(champion_noise, champion_scale)
            row = [i, y, f"{champ:.5f}", f"{score(challenger_noise, challenger_scale):.5f}",
                   f"{champ / champion_scale:.5f}", "control" if i % 2 else "tratado"]
            rows.append(row)
        return self.csv("c.csv", ["id", "target", "v3", "v4", "v3_recal", "grupo"], rows)

    def promote(self, path, *extra):
        return run(PROMOTION, path, "--champion", "v3", "--challenger", "v4", "--n-boot", "100", *extra)

    def test_challenger_claramente_mejor(self):
        r = self.promote(self.cohort())
        self.assertPasses(r)
        self.assertIn("DECISIÓN: challenger", r.stdout)

    def test_mejora_dentro_del_ruido_se_queda_el_champion(self):
        r = self.promote(self.cohort(champion_noise=0.5, challenger_noise=0.5))
        self.assertPasses(r)
        self.assertIn("DECISIÓN: champion", r.stdout)

    def test_recalibrado_gana_si_solo_cambio_el_nivel(self):
        path = self.cohort(champion_noise=0.5, champion_scale=0.5, challenger_noise=0.5, challenger_scale=0.5)
        r = self.promote(path, "--recalibrated", "v3_recal")
        self.assertPasses(r)
        self.assertIn("DECISIÓN: recalibrado", r.stdout)

    def test_challenger_descalibrado_no_gana(self):
        r = self.promote(self.cohort(challenger_scale=0.4))
        self.assertPasses(r)
        self.assertIn("empeora la calibración", r.stdout)
        self.assertIn("DECISIÓN: champion", r.stdout)

    def test_datos_insuficientes(self):
        r = self.promote(self.cohort(n=120))
        self.assertIn("DECISIÓN: champion — datos insuficientes", r.stdout)

    def test_filtro_y_json(self):
        out = self.tmp / "d.json"
        r = self.promote(self.cohort(), "--where", "grupo=control", "--json", out)
        self.assertPasses(r)
        data = json.loads(out.read_text(encoding="utf-8"))
        self.assertEqual(data["decision"], "challenger")
        self.assertEqual(data["n"], 1500)

    def test_columna_inexistente(self):
        r = run(PROMOTION, self.cohort(), "--champion", "v3", "--challenger", "v9")
        self.assertFails(r, "faltan columnas: v9", code=2)

    def test_ks_calculado(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location("promotion", PROMOTION)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        self.assertEqual(mod.ks([0, 0, 1, 1], [0.1, 0.2, 0.3, 0.4]), 1.0)
        self.assertEqual(mod.ks([0, 1, 0, 1], [0.5] * 4), 0.0)
        self.assertEqual(mod.ks([0, 1, 1, 0], [0.1, 0.2, 0.3, 0.4]), 0.5)

    def test_ks_challenger_claramente_mejor(self):
        out = self.tmp / "d.json"
        r = self.promote(self.cohort(), "--metric", "ks", "--json", out)
        self.assertPasses(r)
        self.assertIn("métrica principal: KS", r.stdout)
        self.assertIn("DECISIÓN: challenger — mejora el KS", r.stdout)
        data = json.loads(out.read_text(encoding="utf-8"))
        self.assertEqual(data["metric"], "ks")
        self.assertGreater(data["diff"], 0)
        self.assertEqual(set(data["metrics"]["v4"]), {"auc", "gini", "ks", "cal"})

    def test_ks_dentro_del_ruido_se_queda_el_champion(self):
        r = self.promote(self.cohort(champion_noise=0.5, challenger_noise=0.5), "--metric", "ks")
        self.assertPasses(r)
        self.assertIn("DECISIÓN: champion", r.stdout)

    def split_cohort(self, n=3000, seed=7, cut=0.6, width=0.4):
        """El challenger separa perfecto alrededor de un corte y desordena cada lado:
        sube el KS y baja el AUC respecto de un champion con ruido moderado."""
        import math
        rng = random.Random(seed)
        sig = lambda v: 1 / (1 + math.exp(-(1.5 * v - 2)))  # noqa: E731
        rows = []
        for i in range(n):
            z = rng.gauss(0, 1)
            y = 1 if rng.random() < sig(z) else 0
            champ = sig(z + rng.gauss(0, 0.6))
            chall = sig(cut + width * rng.random() if z > cut else cut - width * rng.random())
            rows.append([i, y, f"{champ:.5f}", f"{chall:.5f}"])
        return self.csv("s.csv", ["id", "target", "v3", "v4"], rows)

    def test_la_metrica_principal_decide(self):
        path = self.split_cohort()
        by_ks = self.promote(path, "--metric", "ks", "--cal-tolerance", "1")
        self.assertIn("DECISIÓN: challenger", by_ks.stdout)
        by_auc = self.promote(path, "--metric", "auc", "--cal-tolerance", "1")
        self.assertIn("DECISIÓN: champion", by_auc.stdout)

    def test_ks_principal_con_auc_secundario_que_empeora(self):
        r = self.promote(self.split_cohort(), "--metric", "ks", "--cal-tolerance", "1",
                         "--secondary-tolerance", "0.005")
        self.assertPasses(r)
        self.assertIn("empeora el AUC más que la tolerancia", r.stdout)
        self.assertIn("DECISIÓN: champion", r.stdout)


class InputsTest(CheckTest):
    CONTRACT = {"tables": {
        "cartera.saldos": {"columns": {"id_cliente": "bigint", "saldo": "decimal|double", "fecha": "date"},
                           "min_rows": 1000, "max_drop": 0.30, "max_staleness_days": 2},
        "aux.campanias": {"columns": {"id": "int"}, "critical": False, "max_staleness_days": 7},
    }}

    def gate(self, schema=None, volumes=None, contract=None, run_date="2026-11-27"):
        schema = schema or [["cartera.saldos", "id_cliente", "BIGINT"], ["cartera.saldos", "saldo", "decimal(18,2)"],
                            ["cartera.saldos", "fecha", "date"], ["aux.campanias", "id", "int"]]
        volumes = volumes or [["cartera.saldos", "2026-11-25", 50000], ["cartera.saldos", "2026-11-26", 51000],
                              ["aux.campanias", "2026-11-26", 40], ["aux.campanias", "2026-11-25", 38]]
        c = self.text("contrato.json", json.dumps(contract or self.CONTRACT))
        s = self.csv("columnas.csv", ["table", "column", "type"], schema)
        v = self.csv("volumenes.csv", ["table", "partition", "rows"], volumes)
        return run(INPUTS, "--contract", c, "--schema", s, "--volumes", v, "--run-date", run_date)

    def test_entradas_sanas(self):
        r = self.gate()
        self.assertPasses(r)
        self.assertIn("VEREDICTO: pasa", r.stdout)

    def test_columna_faltante_y_tipo_distinto(self):
        r = self.gate(schema=[["cartera.saldos", "id_cliente", "varchar(20)"], ["cartera.saldos", "fecha", "date"],
                              ["cartera.saldos", "nueva", "int"], ["aux.campanias", "id", "int"]])
        self.assertFails(r, "faltan columnas: saldo", "id_cliente es varchar(20), se esperaba bigint",
                         "columnas que el contrato no conoce: nueva", "no publicar predicciones")

    def test_caida_de_volumen(self):
        r = self.gate(volumes=[["cartera.saldos", "2026-11-25", 50000], ["cartera.saldos", "2026-11-26", 20000],
                               ["aux.campanias", "2026-11-26", 40]])
        self.assertFails(r, "volumen cae 60%")

    def test_particion_vieja(self):
        self.assertFails(self.gate(run_date="2026-12-05"), "tiene 9 días (máximo 2)")

    def test_tabla_no_critica_solo_advierte(self):
        r = self.gate(volumes=[["cartera.saldos", "2026-11-25", 50000], ["cartera.saldos", "2026-11-26", 51000],
                               ["aux.campanias", "2026-11-10", 40]])
        self.assertPasses(r)
        self.assertIn("WARN  última partición 2026-11-10", r.stdout)

    def test_tabla_inexistente(self):
        contract = {"tables": {"otra.tabla": {"columns": {"id": "int"}}}}
        self.assertFails(self.gate(contract=contract), "no existe en el esquema observado")


class TraceabilityTest(CheckTest):
    def chain(self, lost_in="", fmt=False, n=400):
        """predicción → decisión → resultado; lost_in = canal cuyos resultados no se registran."""
        pred = [[f"P{i}", f"2026-0{1 + i % 3}-15", "web" if i % 2 else "sucursal"] for i in range(n)]
        dec = [[f"P{i}", f"D{i}"] for i in range(n)]
        res = [[f"d{i}" if fmt and i % 10 == 0 else f"D{i}", i % 7 == 0] for i in range(n)
               if not (lost_in and pred[i][2] == lost_in)]
        return (self.csv("pred.csv", ["id_prediccion", "fecha", "canal"], pred),
                self.csv("dec.csv", ["id_prediccion", "id_decision"], dec),
                self.csv("res.csv", ["id_decision", "malo"], res))

    def trace(self, files, *extra):
        pred, dec, res = files
        return run(TRACEABILITY, "--step", f"pred={pred}", "--step", f"dec={dec}", "--step", f"res={res}",
                   "--hop", "pred.id_prediccion=dec.id_prediccion", "--hop", "dec.id_decision=res.id_decision",
                   "--period", "pred.fecha", "--segment", "pred.canal", "--min-rows", "20", *extra)

    def test_cadena_completa(self):
        out = self.tmp / "cobertura.csv"
        r = self.trace(self.chain(), "--out", out)
        self.assertPasses(r)
        self.assertIn("acumulada desde pred: 400/400 = 100.0%", r.stdout)
        self.assertIn("dec → res,2026-01,web", out.read_text(encoding="utf-8"))

    def test_segmento_sin_resultados(self):
        r = self.trace(self.chain(lost_in="web"))
        self.assertFails(r, "dec → res: cobertura 50.0%", "segmento web: cobertura 0.0%")

    def test_periodo_inmaduro_no_se_evalua(self):
        pred, dec, res = self.chain()
        rows = [l for l in res.read_text(encoding="utf-8").splitlines()]
        keep = {f"P{i}" for i in range(400) if 1 + i % 3 != 3}
        dec_ok = {f"D{i}" for i in range(400) if f"P{i}" in keep}
        res.write_text("\n".join([rows[0]] + [l for l in rows[1:] if l.split(",")[0] in dec_ok]) + "\n", encoding="utf-8")
        self.assertFails(self.trace((pred, dec, res)), "período 2026-03")
        r = self.trace((pred, dec, res), "--mature-until", "2026-02")
        self.assertPasses(r)
        self.assertIn("inmaduro", r.stdout)

    def test_clave_con_otro_formato(self):
        self.assertFails(self.trace(self.chain(fmt=True)), "40 claves sin par lo encontrarían normalizando")

    def test_saltos_fuera_de_cadena(self):
        pred, dec, res = self.chain()
        r = run(TRACEABILITY, "--step", f"pred={pred}", "--step", f"dec={dec}", "--step", f"res={res}",
                "--hop", "pred.id_prediccion=dec.id_prediccion", "--hop", "pred.id_prediccion=res.id_decision")
        self.assertFails(r, "tiene que salir de 'dec'", code=2)


if __name__ == "__main__":
    unittest.main()
