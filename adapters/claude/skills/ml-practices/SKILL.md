---
name: ml-practices
description: Buenas prácticas de ML supervisado con datos en el tiempo (clasificación, regresión, ranking), independientes del dominio. Usar al plantear el problem framing de un modelo, armar el universo y las particiones (out-of-time, snapshots, backtesting), revisar data leakage, construir y seleccionar features, definir la spec, baselines y experimentos, buscar hiperparámetros, calibrar, comparar la población de entrenamiento con la de predicción (validación adversarial), diseñar un grupo de control o un piloto, monitorear drift o decidir un reentrenamiento (champion/challenger), revisar trazabilidad o documentar un modelo. Para scores de riesgo crediticio usar credit-scoring-ml; para cobranzas, collections-ml.
---

# Prácticas de ML supervisado

Aplicar esta metodología en cualquier proyecto de ML supervisado. El orden importa: un error en la trazabilidad, el universo o las particiones invalida todo lo posterior.

## Flujo

Seguir `ml-foundations/knowledge/00-flujo.md`. Al empezar una etapa, leer su archivo; no cargar todos de entrada.

| Etapa | Leer |
|---|---|
| Problem framing | `ml-foundations/knowledge/00-flujo.md` |
| Universo, particiones, árbitro intacto | `ml-foundations/knowledge/01-universo-particiones.md` |
| Leakage | `ml-foundations/knowledge/02-leakage.md` |
| Features, faltantes, estabilidad por período, embudo | `ml-foundations/knowledge/03-features.md` |
| Spec, baselines, ablaciones, búsqueda, métricas, calibración | `ml-foundations/knowledge/04-modelado.md` |
| Población de entrenamiento vs. de predicción, sesgo de selección | `ml-foundations/knowledge/05-poblacion-y-sesgo.md` |
| Monitoreo, recalibrar vs. reentrenar, regla de promoción | `ml-foundations/knowledge/06-monitoreo.md` |
| Grupo de control, impacto, pilotos | `ml-foundations/knowledge/07-experimentacion.md` |
| Trazabilidad | `ml-foundations/knowledge/08-trazabilidad.md` |
| Documentación y reproducibilidad | `ml-foundations/knowledge/09-documentacion.md` |

Para la forma de trabajar (archivos de memoria del proyecto, criterios de cierre, una pregunta a la vez), seguir `shared/agent-workflow.md`.

## Reglas que no se negocian

1. Con datos en el tiempo, la validación final es fuera de tiempo. Un split aleatorio solo sirve dentro de train, para tunear.
2. Ninguna variable posterior al momento de la predicción. Ante la duda, preguntar la fecha de disponibilidad antes de usarla.
3. La elegibilidad es idéntica en train, validación y predicción.
4. Toda transformación y todo sampling se ajustan solo con train.
5. El conjunto que decide el veredicto se mira una vez. El early stopping y la búsqueda usan otro conjunto, dentro de train.
6. Siempre hay baselines (ingenuo, regla y modelo sin tunear) y cada experimento cambia una sola cosa.
7. Un desempeño sospechosamente alto o una variable que concentra gran parte de la importancia se tratan como sospecha de leakage hasta demostrar lo contrario.
8. Si el modelo se rebalanceó y la predicción se usa como probabilidad, se recalibra.
9. Un modelo nuevo reemplaza al vigente solo si lo supera por un margen mínimo y no empeora la calibración.
10. Si la acción guiada por el modelo cambia el resultado, el desempeño se mide y el modelo se reentrena sobre el grupo de control.
11. El umbral de decisión lo decide el dueño de la decisión; el modelo entrega la tabla de opciones.
12. Una mejora se comunica con evidencia de desempeño en cohortes maduras, no con cambios en la distribución de las predicciones.

Cuando una de estas reglas impide lo que se pidió, decirlo explícitamente en lugar de seguir en silencio. Cuando la documentación de un repositorio contradice al código, seguir el código y avisar.

## Chequeos ejecutables

Están en `ml-foundations/checks/`. Correrlos antes de reportar métricas de un modelo nuevo.

| Chequeo | Uso |
|---|---|
| Integridad del universo | `python3 ml-foundations/checks/check_universe.py universo.csv --horizon-days N --last-data-date AAAA-MM-DD --id-col <id>` |
| Leakage | `python3 ml-foundations/checks/check_leakage.py --features lista.txt` y sobre el código. Usa `forbidden_columns.txt` de la raíz del proyecto; si no existe, proponer crearlo desde `ml-foundations/checks/forbidden_columns.example.txt` más los nombres reales del proyecto |
| Concentración de importancia | `python3 ml-foundations/checks/check_concentration.py importancias.csv` |
| Estabilidad | `python3 ml-foundations/checks/psi.py ref.csv act.csv --column score`, o `--all-numeric` para CSI |

## Entregables

Al cerrar un modelo, completar `ml-foundations/templates/model-card.md` y `ml-foundations/templates/checklist-validacion.md` en el repositorio del proyecto (copiarlos, no editarlos acá).
