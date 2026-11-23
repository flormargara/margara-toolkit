# Universo, particiones y validación

El modelo se usa en el futuro, sobre poblaciones que todavía no existen. La validación tiene que imitar eso.

## Regla principal

**Si los datos tienen estructura temporal, la validación final es fuera de tiempo (out-of-time).** Un split aleatorio mezcla períodos y sobreestima el desempeño, porque el modelo ve condiciones del mismo período que evalúa. El split aleatorio solo sirve dentro de train, para tunear.

## Target, grano y horizonte

Antes del universo, dejar escrito:

1. **Qué se predice**, en una oración y sin tecnicismos.
2. **Grano:** qué es una fila (persona, cuenta, transacción, producto).
3. **Evento:** qué condición concreta en los datos marca que "pasó".
4. **Horizonte:** en qué ventana después del corte se mide el evento.
5. **Demora hasta la acción:** cuánto pasa entre la predicción y el momento en que se puede actuar. Si la acción llega N días después del corte, el target se mide en `(fecha_corte + demora, fecha_corte + demora + horizonte]`. Si no, el modelo aprende eventos que ocurren antes de poder actuar y que nadie puede evitar.
6. **Tipo:** binario, continuo o conteo; define la agregación.

## Perfil del target

Antes de elegir cortes y particiones, describir el target por período (`checks/target_profile.py`):

- Volumen, eventos y tasa (o media) por período de snapshot, y agregados por trimestre.
- Tendencia y variabilidad de la tasa entre períodos.
- Cambios de régimen: un salto en la tasa suele ser un cambio de definición, de política o de captura, no de comportamiento.
- Períodos con pocos eventos, que no alcanzan para medir nada.

Cerrar con un veredicto: **viable**, **parcial** (viable en una parte del rango o de la población, que se dice cuál) o **descartado**. Un target que cambia de régimen dentro del rango cambia la partición temporal y la calibración.

## Patrón de snapshot

Cada fila del universo es una entidad en una `fecha_corte`:

- **Elegibilidad** medida con datos de hasta `fecha_corte` inclusive. Si la tabla de población no tiene historia, reconstruirla a la fecha; nunca tomar el estado actual.
- **Target** medido en `(fecha_corte, fecha_corte + horizonte]`, desplazado por la demora hasta la acción si la hay.
- **Features** calculadas con datos de hasta `fecha_corte`.
- Fechas siempre parametrizadas (`fecha_corte`, `horizonte_dias`), nunca escritas a mano en la query.
- **Madurez impuesta en la query:** el último corte usable es `último dato completo − horizonte`, para que ninguna fila con target incompleto pueda entrar aunque cambie la fecha de corrida.

**La elegibilidad es idéntica en train, validación y predicción.** El universo de predicción repite el mismo filtro completo, salvo la condición de target. Copiar el filtro de train y "sacarle el target a mano" es la forma más común de romperlo. Verificar además que cada tabla y columna del filtro exista en producción al momento de predecir.

## Esquemas de partición

| Esquema | Cuándo |
|---|---|
| Holdout temporal (train viejo, validación nueva) | Caso base |
| Train / test / validación por período | Cuando hace falta un conjunto para elegir hiperparámetros y otro para el veredicto final |
| Expanding window | El train acumula toda la historia y la validación es siempre el período siguiente |
| Sliding window | Train de ancho fijo W que se desplaza; W chico reacciona más rápido a drift, W grande reduce varianza. Elegir W explícitamente |
| Backtesting (walk-forward) | Varios folds hacia adelante para reportar una distribución de métricas en lugar de un solo número |

Un **gap** entre el final del train y el inicio de la validación evita que compartan condiciones.

## Cinco chequeos de integridad temporal

Obligatorios, contra los datos reales y con veredicto explícito. `checks/check_universe.py` los automatiza.

| Chequeo | Condición |
|---|---|
| Orden temporal | `max(fecha_corte train) < min(fecha_corte validación)` |
| Sin solapamiento de horizonte | `fecha_corte_train + horizonte ≤ fecha_corte_validación`; si no, el target de train mira datos posteriores al corte de validación |
| Elegibilidad consistente | El filtro de población es el mismo en train, validación y predicción |
| Horizonte completo | Ningún snapshot tiene `fecha_corte + horizonte` posterior al último dato completo disponible |
| Sin fuga entre folds | En backtesting, ningún fold de validación reaparece como train de un fold posterior con el horizonte todavía abierto |

Un universo sin veredicto no está listo. Si un chequeo falla, se corrigen fechas o filtros y se repite.

## El árbitro intacto

Hay dos preguntas distintas y necesitan datos distintos:

- **"¿Qué configuración es mejor?"** — muchas miradas (búsqueda de hiperparámetros, selección de variables, early stopping). Vive dentro de train, con su propio esquema de resampling.
- **"¿Qué tan buena es la configuración elegida?"** — una sola mirada, sobre el conjunto de validación final.

Usar el mismo conjunto para el early stopping, para elegir el mejor trial y para reportar el resultado produce un número optimista. El conjunto final se lee una vez por experimento; mirarlo varias veces "para ver cómo viene" lo convierte en un segundo loop de búsqueda.

**Conjunto de selección.** En el esquema train / test / validación por período, el test suele usarse para early stopping, para elegir trials, para elegir la cantidad de variables o para calibrar. Entonces es un conjunto de selección: su métrica es optimista y no se reporta como desempeño. Se rotula así en la ficha, y el desempeño se lee en la validación final. Si el test se usa para varias de esas cosas a la vez, cada uso suma optimismo.

Para proteger el árbitro mecánicamente, cada script de experimento evalúa por defecto el loop de búsqueda y toca la validación final solo con un flag explícito (por ejemplo `--evaluate-arbiter`), una vez por experimento.

Esquemas para la búsqueda dentro de train:

| Esquema | Cuándo |
|---|---|
| K-fold por grupo (por entidad) | Obligatorio si la misma entidad aparece en varios snapshots |
| K-fold estratificado | Clases desbalanceadas y una fila por entidad |
| Folds temporales dentro de train | La estructura temporal importa también dentro de train |
| Nested CV | Dataset chico donde una sola estimación es inestable; escalar a esto solo si la inestabilidad se observa |
| Un solo split reservado dentro de train | Cuando todavía no hay nada que buscar |

## Detalles que rompen la validación

- **Misma entidad en dos particiones.** Si una entidad aparece en varios períodos, elegir una fila por entidad con un hash determinista sobre el identificador (reproducible y sin sesgo de selección), o asignar todas sus filas a la misma partición.
- **Entidades vistas en la validación final.** En producción el modelo puntúa una mezcla de entidades que ya vio en entrenamiento y entidades nuevas. Reportar la validación final en dos vistas: **completa** (todas las entidades del período) y **sin entidades vistas** (excluyendo las que estuvieron en train o test). La completa estima el desempeño real; la otra, la generalización a entidades nuevas. El árbitro es la vista que se parece a la población de predicción, y se decide antes de mirar resultados. Una brecha grande entre las dos indica que el modelo memoriza entidades.
- **Transformaciones ajustadas con toda la muestra.** Imputación, escalado, encoding, binning y selección de variables se ajustan solo con train y se aplican al resto.
- **Decisiones tomadas mirando la validación final.** Cualquier decisión tomada así la contamina.
- **Sampling fuera de train.** Si hace falta submuestrear, se submuestrea solo train, con semilla fija y por snapshot (la misma fracción en cada corte). En SQL, samplear con un hash del identificador y no con una función aleatoria, que no es reproducible entre corridas; así el sampling queda dentro de la receta del dataset (`03b-dataset.md`). Validación y predicción van completas siempre. No samplear también es una decisión que se documenta. En targets multi-label se samplean filas enteras, nunca labels.

## Qué reportar

- Métricas en train, test (rotulado como selección si se usó para elegir) y validación final lado a lado. Una caída grande entre test y validación es una señal, no un detalle.
- La validación final en sus dos vistas: completa y sin entidades vistas.
- Intervalos de confianza (bootstrap) de la métrica principal en la validación final.
- Métricas por período de la validación, no solo el agregado; en backtesting, la distribución entre folds.
- Métricas por segmento relevante para el negocio.
