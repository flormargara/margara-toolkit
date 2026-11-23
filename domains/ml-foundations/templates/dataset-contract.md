# Contrato del dataset — [proyecto] v[versión del dataset]

| Campo | Valor |
|---|---|
| Versión del dataset | |
| Fecha | |
| Receta (archivo y commit) | |
| Universos de entrada (train, validación, scoring) | |

## Columnas

| Columna | Tipo | Rol (clave / target / feature / auxiliar) | Bloque de origen |
|---|---|---|---|
| | | | |

## Particiones

| Partición | Fechas de corte | Filas | Eventos / media del target | Ubicación | Cómo cargarla |
|---|---|---|---|---|---|
| Train | | | | | |
| Validación | | | | | |
| Scoring | | | — | | |

## Sampling

- Estrategia (o "se evaluó y no se sampleó"):
- Qué se sampleó y qué no:
- Fracción y semilla o hash:
- Validación y scoring completos: sí

## Gate (`check_dataset.py`)

| Chequeo | Veredicto | Valor |
|---|---|---|
| Sin duplicados de grano | | |
| Filas preservadas | | |
| Target preservado | | |
| Sin superposición temporal | | |
| Faltantes esperados | | |
| Esquema idéntico | | |

## Nota de paridad

La receta que construyó estas filas es la que reconstruye las filas de scoring en inferencia. Cualquier cambio en la receta genera una versión nueva del dataset y un leaderboard nuevo.
