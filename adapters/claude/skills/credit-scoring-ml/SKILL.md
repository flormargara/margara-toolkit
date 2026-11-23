---
name: credit-scoring-ml
description: Metodología de ML para construir, validar y documentar scores de riesgo crediticio (originación, comportamiento, PD). Usar al definir el target de default, armar particiones out-of-time, revisar data leakage, construir features WoE/IV, entrenar o calibrar un modelo de scoring, calcular PSI/CSI, analizar sesgo de selección o reject inference, o documentar un modelo con su ficha y checklist.
---

# Scores de riesgo crediticio: práctica de ML

Aplicar esta metodología cuando se construye, modifica o valida un score. El orden importa: un error en el target o en las particiones invalida todo lo posterior.

## Flujo

Seguir `references/00-flujo.md`. Al empezar una etapa, leer su archivo de referencia; no cargar todos de entrada.

| Etapa | Leer |
|---|---|
| Definir el target de default | `references/01-definicion-default.md` |
| Armar train / test / OOT | `references/02-particiones-validacion.md` |
| Revisar leakage | `references/03-leakage.md` |
| Features, binning, WoE, IV | `references/04-features.md` |
| Modelo, métricas, calibración, corte | `references/05-modelado-calibracion.md` |
| Aprobados vs. solicitantes | `references/06-sesgo-seleccion.md` |
| PSI/CSI y monitoreo | `references/07-estabilidad-monitoreo.md` |
| Variables sensibles, reason codes | `references/08-equidad-regulacion.md` |
| Documentar | `references/09-documentacion.md` |

## Reglas que no se negocian

1. La validación final es out-of-time. Un split aleatorio solo sirve para tunear.
2. Ninguna variable posterior al punto de decisión. Ante la duda, preguntar la fecha de disponibilidad antes de usarla.
3. Toda transformación se ajusta solo con train.
4. El OOT se mira una vez, al final. Si se usó para decidir algo, avisarlo.
5. Siempre hay un baseline de regresión logística contra el que comparar.
6. AUC > 0.90 o una variable con IV > 0.5 se tratan como sospecha de leakage hasta demostrar lo contrario.
7. El punto de corte lo decide el dueño del riesgo; el modelo entrega la tabla de opciones.

Cuando una de estas reglas impide lo que se pidió, decirlo explícitamente en lugar de seguir en silencio.

## Chequeos ejecutables

- **Leakage:** `python3 scripts/check_leakage.py --features <lista_features.txt>` sobre la lista final, y sobre el código con `python3 scripts/check_leakage.py <archivos>`. Usa `forbidden_columns.txt` de la raíz del proyecto; si no existe, proponer crearlo a partir de `scripts/forbidden_columns.example.txt` adaptado a los nombres reales de las columnas.
- **Estabilidad:** `python3 scripts/psi.py referencia.csv actual.csv --column score`, o `--all-numeric` para CSI por variable. También importable: `from psi import psi`.

Correr el chequeo de leakage antes de reportar cualquier métrica de un modelo nuevo.

## Entregables

Al cerrar un modelo, completar `templates/model-card.md` y `templates/checklist-validacion.md` en el repositorio del proyecto (copiarlos, no editarlos acá). Cada número reportado indica de qué partición sale.
