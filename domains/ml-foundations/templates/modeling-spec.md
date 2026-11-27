# Spec del modelado — [proyecto]

Se escribe y se confirma con quien usa el modelo **antes del primer experimento** (ver `knowledge/04-modelado.md`). Vive en el proyecto como `MODELING_SPEC.md`. Se agrega, no se sobrescribe: un cambio va como entrada nueva con fecha y motivo.

| Campo | Valor |
|---|---|
| Versión del dataset | [ver contrato del dataset] |
| Fecha | |
| Confirmado por | [nombre o rol de quien usa el modelo] |

## 1. Objetivo

- Decisión que apoya, en una oración:
- Tipo de problema: clasificación binaria / multiclase / regresión / ranking
- Uso de la salida: ordenar / número (probabilidad, monto) / umbral de decisión

## 2. Métricas

| Rol | Métrica | Dirección | Por qué |
|---|---|---|---|
| Principal (decide qué experimento gana) | | ↑ / ↓ | [qué costo de error refleja] |
| Diagnóstico | Calibración | | |
| Diagnóstico | Estabilidad por período | | |
| Diagnóstico | Error por segmento: [segmentos] | | |

## 3. Qué es "suficientemente bueno"

- Criterio: [umbral absoluto en la métrica principal] o [superar al modelo vigente o a la regla por un margen mínimo de …]
- Margen mínimo para declarar una mejora (mayor que la dispersión esperada):
- Qué pasa si ningún candidato lo alcanza: [se documenta y se discute; no se baja el criterio en silencio]

## 4. Restricciones

- Interpretabilidad:
- Latencia y tamaño:
- Familias de modelos vetadas o exigidas:
- Variables vetadas (además de `forbidden_columns.txt`):
- Concentración máxima aceptada (`check_concentration.py`):

## 5. Esquema de validación

Cambiarlo después invalida todas las comparaciones anteriores y abre una sección nueva en el leaderboard.

| Conjunto | Períodos | Para qué se usa | Cuántas veces se mira |
|---|---|---|---|
| Búsqueda (dentro de train) | | Folds temporales: elegir experimentos e hiperparámetros, media ± dispersión | Siempre |
| Early stopping | | [subconjunto de train / período de test rotulado como conjunto de selección] | Siempre |
| Árbitro (validación final, fuera de tiempo) | | Veredicto, vista completa y sin entidades vistas | Una vez por experimento |

- Vista del árbitro que decide, según la población de predicción: completa / sin entidades vistas
- Dispersión que se reporta: folds / semillas / bootstrap, con el tamaño de cada conjunto

## 6. Baselines

| Baseline | Definición | Métrica principal (árbitro) |
|---|---|---|
| Ingenuo | | |
| Regla o proceso vigente | | |
| Modelo sin tunear | | |

## 7. Fuera de alcance

- Lo que esta versión no intenta resolver y queda para otra:

## Historial

| Fecha | Cambio | Motivo | Confirmado por |
|---|---|---|---|
| | Versión inicial | | |
