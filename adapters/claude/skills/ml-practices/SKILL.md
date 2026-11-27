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
| ¿Hace falta ML?, problem framing, uso y respaldo | `ml-foundations/knowledge/00-flujo.md` |
| Perfil del target, demora hasta la acción, universo, particiones, árbitro intacto | `ml-foundations/knowledge/01-universo-particiones.md` |
| Leakage, observación vs. afirmación sobre los datos | `ml-foundations/knowledge/02-leakage.md` |
| Features: ideación anclada a fuentes, fabricabilidad, estándar de nombres, faltantes, estabilidad por período, selección sin target y predictiva, embudo | `ml-foundations/knowledge/03-features.md` |
| Dataset: una receta, contrato de bloques, gate de integridad | `ml-foundations/knowledge/03b-dataset.md` |
| Spec, baselines, leaderboard, incertidumbre, búsqueda, métricas, calibración | `ml-foundations/knowledge/04-modelado.md` |
| Población de entrenamiento vs. de predicción, sesgo de selección | `ml-foundations/knowledge/05-poblacion-y-sesgo.md` |
| Monitoreo, referencia, gate de entradas, recalibrar vs. reentrenar, regla de promoción | `ml-foundations/knowledge/06-monitoreo.md` |
| Grupo de control, ficha de impacto, pilotos | `ml-foundations/knowledge/07-experimentacion.md` |
| Trazabilidad | `ml-foundations/knowledge/08-trazabilidad.md` |
| Documentación, ancla con el código, estándar SQL, reproducibilidad y pasar a producción | `ml-foundations/knowledge/09-documentacion.md` |

Para la forma de trabajar (archivos de memoria del proyecto, criterios de cierre, una pregunta a la vez, revisión en dos niveles, cómo escribir skills), seguir `shared/agent-workflow.md`.

## Reglas que no se negocian

1. Con datos en el tiempo, la validación final es fuera de tiempo. Un split aleatorio solo sirve dentro de train, para tunear.
2. Ninguna variable posterior al momento de la predicción. Ante la duda, preguntar la fecha de disponibilidad antes de usarla.
3. La elegibilidad es idéntica en train, validación y predicción.
4. Toda transformación y todo sampling se ajustan solo con train.
5. El conjunto que decide el veredicto se mira una vez. El early stopping, la búsqueda y la selección de variables con target usan otro conjunto, dentro de train. Un test usado para elegir se rotula como conjunto de selección.
6. Siempre hay baselines (ingenuo, regla y modelo sin tunear) y cada experimento cambia una sola cosa, con su fila en el leaderboard. Cada métrica va con su dispersión; una diferencia menor que la dispersión es un empate.
7. Un desempeño sospechosamente alto o una variable que concentra gran parte de la importancia se tratan como sospecha de leakage hasta demostrar lo contrario.
8. Si el modelo se rebalanceó y la predicción se usa como probabilidad, se recalibra.
9. Un modelo nuevo reemplaza al vigente solo si lo supera por un margen mínimo y no empeora la calibración.
10. Si la acción guiada por el modelo cambia el resultado, el desempeño se mide y el modelo se reentrena sobre el grupo de control.
11. El umbral de decisión lo decide el dueño de la decisión; el modelo entrega la tabla de opciones.
12. Una mejora se comunica con evidencia de desempeño en cohortes maduras, no con cambios en la distribución de las predicciones.
13. Train, validación y scoring salen de la misma receta con distinto universo.
14. Si la acción llega después de la predicción, el target se mide desde que se puede actuar.

Cuando una de estas reglas impide lo que se pidió, decirlo explícitamente en lugar de seguir en silencio. Cuando la documentación de un repositorio contradice al código, seguir el código y avisar.

## Chequeos ejecutables

Están en `ml-foundations/checks/`. Correrlos antes de reportar métricas de un modelo nuevo.

| Chequeo | Uso |
|---|---|
| Perfil del target | `python3 ml-foundations/checks/target_profile.py universo.csv --date-col fecha_corte --target-col target` |
| Integridad del universo | `python3 ml-foundations/checks/check_universe.py universo.csv --horizon-days N --last-data-date AAAA-MM-DD --id-col <id>` (con `--arbiter-overlap` si la validación final se reporta completa y sin entidades vistas) |
| Integridad del dataset | `python3 ml-foundations/checks/check_dataset.py --split train=m_train.csv --split val=m_val.csv --universe train=u_train.csv --universe val=u_val.csv --id-col <id> --target-cols target` |
| Leakage | `python3 ml-foundations/checks/check_leakage.py --features lista.txt` y sobre el código. Usa `forbidden_columns.txt` de la raíz del proyecto; si no existe, proponer crearlo desde `ml-foundations/checks/forbidden_columns.example.txt` más los nombres reales del proyecto |
| Concentración de importancia | `python3 ml-foundations/checks/check_concentration.py importancias.csv` |
| Nombres de features | `python3 ml-foundations/checks/check_feature_names.py lista.txt` (o el CSV del dataset con `--ignore` para claves y target) |
| Estabilidad | `python3 ml-foundations/checks/psi.py ref.csv act.csv --column score`, o `--all-numeric` para CSI |
| Promoción | `python3 ml-foundations/checks/promotion.py cohorte.csv --champion <col> --challenger <col> --recalibrated <col>` (con `--where grupo=control` si la acción cambia el resultado). Decide, no falla: la decisión se reporta tal cual |

## Entregables

Copiar al repositorio del proyecto (no editarlos acá):

- En la etapa de features: `ml-foundations/templates/feature-handoff.md`.
- Antes del problem framing: `ml-foundations/templates/discovery.md`.
- Antes del primer experimento: `ml-foundations/templates/modeling-spec.md`.
- Durante el modelado: `ml-foundations/templates/dataset-contract.md` y `ml-foundations/templates/leaderboard.md`.
- Al cerrar el modelo: `ml-foundations/templates/model-card.md` y `ml-foundations/templates/checklist-validacion.md`.
- Antes del despliegue: `ml-foundations/templates/ficha-impacto.md`.
