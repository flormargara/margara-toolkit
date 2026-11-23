# Modelado y calibración

## Spec antes de modelar

Antes del primer experimento, dejar escrito y confirmado con quien usa el modelo:

1. Objetivo de negocio en una oración (qué decisión apoya).
2. Tipo de problema: clasificación binaria o multiclase, regresión, ranking, series de tiempo.
3. Métrica principal: la que decide qué experimento gana. Tiene que reflejar el costo real de cada tipo de error, no el default de la librería.
4. Métricas de diagnóstico: calibración, estabilidad temporal, error por segmento.
5. Qué es "suficientemente bueno": un umbral absoluto o superar al modelo vigente por un margen mínimo. Sin esto no hay criterio para terminar.
6. Restricciones: interpretabilidad, latencia, tamaño de datos, familias de modelos vetadas.
7. Esquema de validación (ver `01-universo-particiones.md`): cuál es el árbitro y cómo se busca dentro de train. Cambiarlo después invalida todas las comparaciones previas.

## Baselines primero

Ningún modelo se evalúa en abstracto: se reporta la diferencia contra los baselines en la métrica principal. Tres baselines:

1. **Ingenuo:** la predicción más simple honesta (media, mediana, clase mayoritaria, tasa promedio). Mide qué tan difícil es el problema.
2. **Regla:** una heurística con 1-2 variables fuertes que una persona podría escribir, o el proceso vigente si existe. Si no existe, proponer una.
3. **Primer modelo sin tunear:** el más simple que use las variables disponibles sin feature engineering pesado (un modelo lineal o un GBM con hiperparámetros por defecto, que maneja faltantes de forma nativa).

Un modelo más complejo tiene que ganarles en la validación final por un margen que justifique su costo. Si la regla gana, se documenta y se discute antes de seguir.

## Experimentos como ablaciones

Cada experimento cambia **una sola cosa** respecto del líder vigente (una variable nueva, otro algoritmo, otro tratamiento de faltantes), para poder atribuir la diferencia. Cada uno queda registrado con su resultado y un veredicto (✅ aceptado, ❌ descartado, ⚠️ requiere revisión). Antes de aceptar un resultado, revisar: leakage, sobreajuste (brecha train-validación mayor que la del baseline), inestabilidad entre folds o períodos, desbalance no tratado en la métrica y error concentrado en un segmento.

## Búsqueda de hiperparámetros

- La búsqueda vive dentro de train (ver el árbitro intacto). El early stopping usa un subconjunto de train, no el conjunto con el que se va a reportar.
- **Penalizar el sobreajuste y la concentración**, no solo maximizar la métrica:
  `score = métrica_val − a · brecha(train, val) − b · exceso_de_concentración − c · participación_de_la_variable_principal`.
  Entre configuraciones con métrica casi igual, elegir la de menor sobreajuste.
- Rangos de hiperparámetros más conservadores cuanto más chico es el dataset.
- Abortar la búsqueda temprano si las primeras pruebas fallan todas: suele indicar un problema de datos, no de hiperparámetros.

## Métricas

**Clasificación**

| Métrica | Mide | Comentario |
|---|---|---|
| AUC-ROC | Capacidad de ordenar | Reportar con intervalo de confianza |
| KS | Máxima separación entre clases | Complementa al AUC |
| AUC-PR | Desempeño en la clase minoritaria | Útil con eventos raros |
| Brier, log-loss | Calidad de las probabilidades | Importan si la probabilidad se usa como número |
| Calibración por decil | Probabilidad estimada vs. observada | Obligatoria si la probabilidad se usa como número |
| Lift / captura en el top-k | Valor en la parte que se va a accionar | Cuando solo se actúa sobre un porcentaje de la población |

No usar accuracy con clases desbalanceadas.

**Regresión:** MAE (robusta), RMSE (penaliza errores grandes), error por tramo del valor real y por segmento, histograma de predicción vs. real. Si el target es asimétrico (ingresos, montos), evaluar en escala logarítmica o por percentiles además de la escala original.

## Segmentación

Segmentar (un modelo por grupo) solo si mejora:

1. Proponer esquemas de segmentación con sentido de negocio y suficientes casos por segmento.
2. Construir un modelo rápido sin segmentar como referencia y uno rápido por segmento.
3. Adoptar la segmentación solo si mejora a la referencia en un margen relevante (por ejemplo 5% de lift) en la validación final.

## Calibración

- Un modelo puede ordenar bien y estar mal calibrado. Si la probabilidad se usa como número, calibrar.
- Calibrar con datos que no se usaron para entrenar (Platt o isotónica sobre un conjunto separado).
- Verificar la calibración en la validación final y por segmento. Si el nivel del evento cambió entre desarrollo y validación, puede hacer falta recalibrar el nivel sin reentrenar.
- Si el score solo se usa para ordenar, decirlo explícitamente y no presentarlo como probabilidad.

## Desbalance de clases

- Para ordenar no hace falta rebalancear. Preferir ajustar el umbral de decisión a modificar la muestra.
- Rebalancear (sobremuestreo, submuestreo, pesos de clase, `scale_pos_weight`, `is_unbalance`) **distorsiona las probabilidades**. Si después el score se usa como probabilidad, recalibrarlo y verificar la calibración por decil.

## Umbral de decisión

El umbral es una decisión de negocio, no del modelo. Presentar para cada umbral posible el volumen accionado, la tasa del evento esperada en cada lado y, si se tiene, el valor económico. La elección final la toma el dueño de la decisión.
