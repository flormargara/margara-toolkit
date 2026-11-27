# Golden rules de ml-foundations

Catálogo de reglas de `domains/ml-foundations` en el formato de golden rules de ai-mllc. No se edita en el proyecto: se compone con `adapters/mllc/compose.py`. Cada regla remite al archivo del toolkit que la explica. Los chequeos viven en `~/projects/margara-toolkit/domains/ml-foundations/checks/`; el código de salida 0 es `cumple`, 1 es `no_cumple`, y si no se pudo correr por falta de insumos es `evidencia_insuficiente`.

## ml-hace-falta-ml (v1)

- fuerza: alerta
- etapa: intake
- mecanismo: discusion
- estado: active

Antes de aceptar la iniciativa, discutir con el Data Scientist si hace falta un modelo: si hay una decisión periódica y repetible, si una regla simple ya captura el valor (comparar por valor, no por cobertura) y si existe un target histórico con calidad razonable. Registrar la respuesta en el frame. Ver `domains/ml-foundations/knowledge/00-flujo.md`, sección "¿Hace falta ML?".

## ml-uso-y-respaldo (v1)

- fuerza: alerta
- etapa: intake
- mecanismo: discusion
- estado: active

El frame dice quién consume la salida, con qué frecuencia, latencia y formato, qué pasa si el modelo falla o no está disponible (respaldo, y si el sistema falla abierto o cerrado) y quién mantiene cada tramo. Lo que no se sabe queda como desconocido, no se inventa. Ver `00-flujo.md`, "Uso del modelo".

## ml-demora-hasta-la-accion (v1)

- fuerza: alerta
- etapa: observe
- mecanismo: discusion
- estado: active

Preguntar cuánto pasa entre la predicción y el momento en que se puede actuar. Si hay demora, el target se mide en `(fecha_corte + demora, fecha_corte + demora + horizonte]`. Registrar la demora (aunque sea cero) junto a la frase del target. Ver `01-universo-particiones.md`.

## ml-perfil-del-target (v1)

- fuerza: alerta
- etapa: observe
- mecanismo: check_determinista
- estado: active

Antes de fijar cortes y particiones, correr `python3 target_profile.py <universo.csv> --date-col fecha_corte --target-col <target>` y presentar la tabla por período, los saltos y el veredicto. Un veredicto parcial se acepta solo si se dice qué rango es viable y por qué. Ver `01-universo-particiones.md`, "Perfil del target".

## ml-integridad-temporal (v1)

- fuerza: bloqueante
- etapa: observe
- mecanismo: check_determinista
- estado: active

Correr `python3 check_universe.py <universo.csv> --horizon-days <h> --last-data-date <AAAA-MM-DD> --id-col <id>` sobre el resultado real de las queries de universo (una columna `split` con train, test, val). Si la validación final se reporta en dos vistas, agregar `--arbiter-overlap`. Cualquier FAIL es `no_cumple`. Ver `01-universo-particiones.md`.

## ml-validacion-fuera-de-tiempo (v1)

- fuerza: bloqueante
- etapa: observe
- mecanismo: atestacion
- estado: active

Con datos en el tiempo, la validación final es un período posterior a train, no un split aleatorio. Atestar con las fechas de corte de cada partición. Elegir antes de mirar resultados si el árbitro es la vista completa o la vista sin entidades vistas en train.

## ml-elegibilidad-identica (v1)

- fuerza: bloqueante
- etapa: observe
- mecanismo: atestacion
- estado: active

El filtro de población es el mismo en train, validación y predicción, salvo la condición de target. Atestar mostrando el filtro de cada query lado a lado y que cada tabla y columna del filtro existe en producción al momento de predecir. Copiar el filtro de train y sacarle el target a mano no cumple.

## ml-sin-columnas-prohibidas (v1)

- fuerza: bloqueante
- etapa: features
- mecanismo: check_determinista
- estado: active

Correr `python3 check_leakage.py --features <lista_de_features.txt>` y sobre el código de features. Usa el `forbidden_columns.txt` de la raíz del proyecto; si no existe, es `evidencia_insuficiente` hasta crearlo desde `forbidden_columns.example.txt` y la lista del dominio. Ver `02-leakage.md`.

## ml-disponibilidad-de-variables (v1)

- fuerza: alerta
- etapa: features
- mecanismo: atestacion
- estado: active

Cada variable candidata tiene en el diccionario su fuente, su fecha de disponibilidad respecto del momento de la predicción y si existe en producción. El significado de una columna se afirma con su procedencia; el nombre de la columna no alcanza. Ver `02-leakage.md`.

## ml-ideas-ancladas-a-fuentes (v1)

- fuerza: alerta
- etapa: features
- mecanismo: atestacion
- estado: active

Cada feature priorizada tiene en el handoff su mecanismo de negocio, una fuente verificada (tabla, columnas, grano, joins), su temporalidad respecto de la fecha de corte y la evidencia que la respaldó. Una idea sin fuente queda en el backlog como pendiente, no se prioriza. El universo y la fecha de corte acordados no se cambian para mejorar la cobertura. Ver `03-features.md`, "Ideación", y `templates/feature-handoff.md`.

## ml-afirmacion-material-confirmada (v1)

- fuerza: bloqueante
- etapa: features
- mecanismo: discusion
- estado: active

Una afirmación material sobre los datos (qué significa una columna, un código o un nulo; que dos tablas se relacionan) que cambia una fuente, un join, el universo, un filtro, una unidad o una moneda se confirma con el Data Scientist o con documentación del dueño de la fuente antes de usarla. Un nombre de columna, un tipo compatible o una tasa de match no alcanzan. Ver `02-leakage.md`, "Observación y afirmación".

## ml-nombres-de-features (v1)

- fuerza: sugerencia
- etapa: features
- mecanismo: check_determinista
- estado: active

Correr `python3 check_feature_names.py <lista_de_features.txt>` (o el CSV del dataset con `--ignore` para las claves y el target). Los nombres siguen `FUENTE_DOMINIO_OPERACION_DESCRIPCION_VENTANA` y el tipo de cada feature sale de su operación. Ver `03-features.md`, "Nombres".

## ml-seleccion-sin-target-en-features (v1)

- fuerza: bloqueante
- etapa: features
- mecanismo: atestacion
- estado: active

En la etapa de features, la selección usa solo criterios sin target (cobertura, varianza, leakage estructural, redundancia, estabilidad de distribución) y nunca abre la columna del target. Lo que mira el target (IV, relación con el target, Boruta, importancias) es selección predictiva y pertenece al modelado, dentro de train. Ver `03-features.md`, "Dos modos".

## ml-integridad-del-dataset (v1)

- fuerza: bloqueante
- etapa: dataset
- mecanismo: check_determinista
- estado: active

Correr `python3 check_dataset.py --split train=<m_train> --split val=<m_val> [--split score=<m_score>] --universe train=<u_train> --universe val=<u_val> --id-col <id> --target-cols <targets>` sobre las exportaciones reales. Sin `--universe` no se verifican filas ni target preservados: eso es `evidencia_insuficiente`. Ver `03b-dataset.md`.

## ml-una-receta (v1)

- fuerza: bloqueante
- etapa: dataset
- mecanismo: atestacion
- estado: active

Train, validación y scoring salen de la misma receta con distinto universo de entrada; no hay tres lógicas paralelas. Atestar con la receta y los tres universos que la alimentan, y escribir la nota de paridad en el contrato del dataset (`templates/dataset-contract.md`).

## ml-sin-credenciales-en-artefactos (v1)

- fuerza: bloqueante
- etapa: dataset
- mecanismo: check_determinista
- estado: active

Ningún dataset, query, script o log bajo la carpeta de la iniciativa contiene una credencial: contraseñas, claves de acceso, tokens o cadenas de conexión con secretos. Buscar esos patrones antes de proponer el cierre; cualquier coincidencia es `no_cumple`. Los secretos se referencian por el nombre de su entrada en el gestor de secretos.

## ml-baselines (v1)

- fuerza: bloqueante
- etapa: model
- mecanismo: atestacion
- estado: active

Antes de cualquier otro experimento existen los tres baselines: ingenuo, regla (o el proceso vigente) y el primer modelo sin tunear, medidos en la métrica principal del spec. Cada experimento posterior se reporta como diferencia contra ellos. Ver `04-modelado.md`.

## ml-arbitro-una-vez (v1)

- fuerza: bloqueante
- etapa: model
- mecanismo: atestacion
- estado: active

La validación final se lee una vez por experimento. El early stopping, la búsqueda de hiperparámetros y la selección predictiva usan otro conjunto, dentro de train. Si se usó un período de test para elegir, se rotula como conjunto de selección y su métrica no se presenta como desempeño. Ver `01-universo-particiones.md`, "El árbitro intacto".

## ml-leaderboard (v1)

- fuerza: alerta
- etapa: model
- mecanismo: atestacion
- estado: active

Cada experimento cambia una sola cosa respecto de su base y tiene su fila en el leaderboard con su base, sus métricas y su veredicto. No se borran filas. Solo se comparan experimentos de la misma versión del dataset. Ver `04-modelado.md` y `templates/leaderboard.md`.

## ml-incertidumbre-de-metricas (v1)

- fuerza: alerta
- etapa: model
- mecanismo: atestacion
- estado: active

Cada cifra de desempeño va con cuánto podría moverse (dispersión entre folds, semillas o remuestreos, o un intervalo) y el tamaño del conjunto en que se midió. Una diferencia entre candidatos menor que esa dispersión es un empate.

## ml-concentracion-de-importancia (v1)

- fuerza: alerta
- etapa: model
- mecanismo: check_determinista
- estado: active

Correr `python3 check_concentration.py <importancias.csv>` sobre las importancias SHAP del líder. Si falla, revisar leakage antes de seguir; una concentración aceptada se justifica por escrito.

## ml-diagnostico-antes-de-tunear (v1)

- fuerza: sugerencia
- etapa: model
- mecanismo: discusion
- estado: active

Antes de abrir una búsqueda de hiperparámetros, decir qué muestra el líder: brecha grande entre train y validación (tunear puede ayudar) o techo plano entre familias y ablaciones (el límite está en features o universo). Primero un estudio corto; uno largo solo si el corto mostró ganancia.

## ml-recalibrar-tras-rebalanceo (v1)

- fuerza: bloqueante
- etapa: model
- mecanismo: atestacion
- estado: active

Si el entrenamiento rebalanceó clases (pesos, sobremuestreo o submuestreo) y la predicción se usa como probabilidad, se recalibra con datos no usados para entrenar y se muestra la calibración por decil en la validación final.

## ml-estabilidad-de-la-prediccion (v1)

- fuerza: alerta
- etapa: model
- mecanismo: check_determinista
- estado: active

Correr `python3 psi.py <scores_desarrollo.csv> <scores_validacion.csv> --column <score> --fail-above 0.25`. Un PSI mayor a 0.25 entre desarrollo y validación final se explica antes de cerrar.

## ml-poblacion-comparada (v1)

- fuerza: alerta
- etapa: model
- mecanismo: atestacion
- estado: active

La población de entrenamiento se compara con la de predicción (por ejemplo, con validación adversarial) y se documenta para qué población vale el desempeño medido. Si la corrección filtra también la validación, se reporta además el resultado sin filtrar. Ver `05-poblacion-y-sesgo.md`.

## ml-grupo-de-control (v1)

- fuerza: bloqueante
- etapa: model
- mecanismo: atestacion
- estado: active

Si la acción guiada por el modelo cambia el resultado, el modelo se entrena y su discriminación se mide solo sobre el grupo de control. Ver `07-experimentacion.md`.

## ml-regla-de-promocion (v1)

- fuerza: bloqueante
- etapa: deploy
- mecanismo: atestacion
- estado: active

Un modelo reemplaza al vigente solo si mejora la métrica principal por un margen mínimo acordado o con un intervalo bootstrap de la diferencia que excluye cero, y no empeora la calibración. Una mejora mayor que cero no alcanza. La evidencia es la salida de `python3 promotion.py <cohorte.csv> --champion <col> --challenger <col> --recalibrated <col> --metric <auc|ks>` (la métrica principal de la spec; con `--secondary-tolerance` si la secundaria no puede empeorar) sobre una cohorte madura que ninguno usó para entrenar. Ver `06-monitoreo.md`.

## ml-monitoreo-referido (v1)

- fuerza: alerta
- etapa: deploy
- mecanismo: atestacion
- estado: active

El plan de monitoreo compara el drift contra los artefactos del modelo vigente y el desempeño contra la validación final de esta versión, no contra test. Un desvío es hallazgo solo en cohortes maduras y con un intervalo que excluye lo esperado. Ver `06-monitoreo.md`.

## ml-gate-de-entradas (v1)

- fuerza: alerta
- etapa: deploy
- mecanismo: discusion
- estado: active

Acordar con el Data Scientist el control de cada tabla de entrada antes de cada corrida (esquema, volumen, frescura), qué pasa si falla (por defecto no se publican predicciones) y quién recibe el aviso. Registrarlo en el plan de despliegue. El control puede ser `python3 check_inputs.py --contract contrato.json --schema columnas.csv --volumes volumenes.csv` como primer paso del pipeline, con el contrato versionado junto al código.

## ml-camino-de-reversion (v1)

- fuerza: alerta
- etapa: deploy
- mecanismo: discusion
- estado: active

Antes de aceptar el plan de despliegue, acordar cómo se apaga o revierte el modelo: quién puede hacerlo, a qué vuelve el sistema y en cuánto tiempo.

## ml-ficha-de-impacto (v1)

- fuerza: alerta
- etapa: deploy
- mecanismo: discusion
- estado: active

Antes de aceptar el despliegue, existe una ficha de impacto en borrador con el KPI, el tipo de contrafactual y la ventana de maduración. Si no hay contrafactual, se dice y queda como pendiente diseñar un holdout. Ver `07-experimentacion.md` y `templates/ficha-impacto.md`.
