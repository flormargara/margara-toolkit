# Universo, particiones y validación

En riesgo de crédito el modelo se usa en el futuro, sobre poblaciones que todavía no existen. La validación tiene que imitar eso.

## Regla principal

**La validación final es out-of-time (OOT) y es obligatoria.** Un split aleatorio mezcla meses y sobreestima el desempeño, porque el modelo ve condiciones económicas, políticas y campañas del mismo período que evalúa. El split aleatorio solo sirve dentro de train, para tunear.

## Patrón de snapshot

Cada fila del universo es una entidad en una `fecha_corte`:

- **Elegibilidad** medida con datos de hasta `fecha_corte` inclusive. Si la tabla de población no tiene historia, reconstruirla a la fecha; nunca tomar el estado actual.
- **Target** medido en `(fecha_corte, fecha_corte + horizonte]`.
- **Features** calculadas con datos de hasta `fecha_corte`.
- Fechas siempre parametrizadas (`fecha_corte`, `horizonte_dias`), nunca escritas a mano en la query.

**La elegibilidad es idéntica en train, validación y scoring.** El universo de predicción repite el mismo filtro completo, salvo la condición de target. Copiar el filtro de train y "sacarle el target a mano" es la forma más común de romperlo. Verificar además que cada tabla y columna del filtro exista en producción al momento de scorear.

## Esquemas de partición

| Esquema | Cuándo |
|---|---|
| Holdout temporal (train viejo, validación nueva) | Caso base |
| Train / test / validación por período (por ejemplo train hasta t−4, test t−3, validación t−2 a t) | Cuando hace falta un conjunto para elegir hiperparámetros y otro para el veredicto final |
| Expanding window | El train acumula toda la historia y la validación es siempre el período siguiente |
| Sliding window | Train de ancho fijo W que se desplaza; W chico reacciona más rápido a drift, W grande reduce varianza. Elegir W explícitamente |
| Backtesting (walk-forward) | Varios folds hacia adelante para reportar una distribución de métricas en lugar de un solo número |

Un **gap** de meses entre el final del train y el inicio de la validación evita que compartan condiciones.

## Cinco chequeos de integridad temporal

Obligatorios, contra los datos reales y con veredicto explícito. `checks/check_universe.py` los automatiza.

| Chequeo | Condición |
|---|---|
| Orden temporal | `max(fecha_corte train) < min(fecha_corte validación)` |
| Sin solapamiento de horizonte | `fecha_corte_train + horizonte ≤ fecha_corte_validación`; si no, el target de train mira datos posteriores al corte de validación |
| Elegibilidad consistente | El filtro de población es el mismo en train, validación y scoring |
| Horizonte completo | Ningún snapshot tiene `fecha_corte + horizonte` posterior al último dato completo disponible |
| Sin fuga entre folds | En backtesting, ningún fold de validación reaparece como train de un fold posterior con el horizonte todavía abierto |

Un universo sin veredicto no está listo. Si un chequeo falla, se corrigen fechas o filtros y se repite.

## El árbitro intacto

Hay dos preguntas distintas y necesitan datos distintos:

- **"¿Qué configuración es mejor?"** — muchas miradas (búsqueda de hiperparámetros, selección de variables, early stopping). Vive dentro de train, con su propio esquema de resampling.
- **"¿Qué tan buena es la configuración elegida?"** — una sola mirada, sobre el conjunto de validación final.

Usar el mismo conjunto para el early stopping, para elegir el mejor trial y para reportar el resultado produce un número optimista. El conjunto final se lee una vez por experimento; mirarlo varias veces "para ver cómo viene" lo convierte en un segundo loop de búsqueda.

Esquemas para la búsqueda dentro de train:

| Esquema | Cuándo |
|---|---|
| K-fold por grupo (por persona) | Obligatorio si la misma persona aparece en varios snapshots |
| K-fold estratificado | Clases desbalanceadas y una fila por entidad |
| Folds temporales dentro de train | La estructura temporal importa también dentro de train |
| Un solo split reservado dentro de train | Cuando todavía no hay nada que buscar |

## Detalles que rompen la validación

- **Misma persona en dos particiones.** Si una persona aparece en varios períodos, elegir una fila por persona con un hash determinista sobre el identificador (reproducible y sin sesgo de selección), o asignar todas sus filas a la misma partición. Excluir de validación a las personas que estuvieron en train o test.
- **Transformaciones ajustadas con toda la muestra.** Binning, WoE, imputación, escalado y selección de variables se ajustan solo con train y se aplican al resto.
- **Selección de variables mirando el OOT.** Cualquier decisión tomada mirando el OOT lo contamina.
- **Cohortes inmaduras en el OOT** (ver `01-definicion-default.md`).
- **Sampling fuera de train.** Si hace falta submuestrear, se submuestrea solo train, con semilla fija y por snapshot (la misma fracción en cada corte). Validación y scoring van completos siempre. No samplear también es una decisión que se documenta.

## Qué reportar

- Métricas en train, test y OOT lado a lado. Una caída grande de test a OOT es una señal, no un detalle.
- Intervalos de confianza (bootstrap) de AUC/Gini y KS en el OOT.
- Métricas por cohorte mensual del OOT, no solo el agregado; en backtesting, la distribución entre folds.
- Métricas por segmento relevante (producto, canal, región, cliente nuevo vs. existente).
