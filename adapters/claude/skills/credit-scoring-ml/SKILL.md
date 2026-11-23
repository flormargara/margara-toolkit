---
name: credit-scoring-ml
description: Metodología de ML para construir, validar, desplegar y monitorear scores de riesgo crediticio (originación, comportamiento, PD, ratings). Usar al definir el target de default o hacer análisis de roll rate, armar el universo y las particiones out-of-time, revisar data leakage, construir y seleccionar features (WoE/IV, estabilidad), entrenar o calibrar un modelo, construir ratings, calcular PSI/CSI, analizar sesgo de selección o diferencias entre población de entrenamiento y de predicción, diseñar grupos de control, revisar trazabilidad, decidir un reentrenamiento (champion/challenger) o documentar un modelo. Para modelos de cobranzas usar collections-ml.
---

# Scores de riesgo crediticio: práctica de ML

Aplicar esta metodología cuando se construye, modifica, valida o monitorea un score. El orden importa: un error en la trazabilidad, el target o las particiones invalida todo lo posterior.

## Flujo

Seguir `references/00-flujo.md`. Al empezar una etapa, leer su archivo; no cargar todos de entrada.

| Etapa | Leer |
|---|---|
| Verificar que la cadena evaluación → desempeño se pueda reconstruir | `references/12-trazabilidad.md` |
| Definir el target (roll rate, ventana, 3R, monto mínimo) | `references/01-definicion-default.md` |
| Universo, particiones, árbitro intacto | `references/02-particiones-validacion.md` |
| Leakage | `references/03-leakage.md` |
| Features, faltantes, estabilidad por período, embudo | `references/04-features.md` |
| Spec, baselines, ablaciones, búsqueda, calibración, segmentación | `references/05-modelado-calibracion.md` |
| Aprobados vs. solicitantes, población de entrenamiento vs. de predicción | `references/06-sesgo-seleccion.md` |
| Monitoreo, recalibrar vs. reentrenar, regla de promoción | `references/07-estabilidad-monitoreo.md` |
| Variables sensibles, reason codes | `references/08-equidad-regulacion.md` |
| Documentación y reproducibilidad | `references/09-documentacion.md` |
| Bandas de rating | `references/10-ratings.md` |
| Grupo de control, impacto, pilotos | `references/11-experimentacion.md` |

Para la forma de trabajar (archivos de memoria del proyecto, criterios de cierre, una pregunta a la vez), seguir `shared/agent-workflow.md`.

## Reglas que no se negocian

1. La validación final es out-of-time. Un split aleatorio solo sirve dentro de train, para tunear.
2. Ninguna variable posterior al punto de decisión. Ante la duda, preguntar la fecha de disponibilidad antes de usarla.
3. La elegibilidad es idéntica en train, validación y scoring.
4. Toda transformación se ajusta solo con train. El sampling, también solo en train.
5. El conjunto que decide el veredicto se mira una vez. El early stopping y la búsqueda de hiperparámetros usan otro conjunto, dentro de train.
6. Siempre hay baselines (ingenuo, regla y modelo sin tunear) y cada experimento cambia una sola cosa.
7. AUC > 0.90, una variable con IV > 0.5 o una variable que concentra gran parte de la importancia se tratan como sospecha de leakage hasta demostrar lo contrario.
8. Si el score se rebalanceó y se va a usar como probabilidad, se recalibra.
9. Un modelo nuevo reemplaza al vigente solo si lo supera por un margen mínimo y no empeora la calibración por rating.
10. Si la acción guiada por el modelo cambia el resultado, el desempeño se mide y el modelo se reentrena sobre el grupo de control.
11. El punto de corte lo decide el dueño del riesgo; el modelo entrega la tabla de opciones.
12. Una mejora del modelo se comunica con evidencia de desempeño en cohortes maduras, no con cambios en la distribución de ratings.

Cuando una de estas reglas impide lo que se pidió, decirlo explícitamente en lugar de seguir en silencio. Cuando la documentación de un repositorio contradice al código, seguir el código y avisar.

## Chequeos ejecutables

Están en `scripts/`. Correrlos antes de reportar métricas de un modelo nuevo.

| Chequeo | Uso |
|---|---|
| Integridad del universo | `python3 scripts/check_universe.py universo.csv --horizon-days N --last-data-date AAAA-MM-DD --id-col <id>` |
| Leakage | `python3 scripts/check_leakage.py --features lista.txt` y sobre el código. Usa `forbidden_columns.txt` de la raíz del proyecto; si no existe, proponer crearlo desde `scripts/forbidden_columns.example.txt` |
| Concentración de importancia | `python3 scripts/check_concentration.py importancias.csv` |
| Estabilidad | `python3 scripts/psi.py ref.csv act.csv --column score`, o `--all-numeric` para CSI |

## Entregables

Al cerrar un modelo, completar `templates/model-card.md` y `templates/checklist-validacion.md` en el repositorio del proyecto (copiarlos, no editarlos acá). Cada número reportado indica de qué partición sale.
