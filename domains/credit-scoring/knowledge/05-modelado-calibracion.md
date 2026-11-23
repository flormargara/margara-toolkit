# Modelado y calibración

## Spec antes de modelar

Antes del primer experimento, dejar escrito y confirmado con quien usa el modelo:

1. Objetivo de negocio en una oración (qué decisión apoya).
2. Métrica principal: la que decide qué experimento gana. Tiene que reflejar el costo real de cada tipo de error.
3. Métricas de diagnóstico: calibración, estabilidad temporal, error por segmento.
4. Qué es "suficientemente bueno": un umbral absoluto o superar al modelo vigente por un margen mínimo. Sin esto no hay criterio para terminar.
5. Restricciones: interpretabilidad, latencia, familias de modelos vetadas.
6. Esquema de validación (ver `02-particiones-validacion.md`): cuál es el árbitro y cómo se busca dentro de train.

## Baselines primero

Ningún modelo se evalúa en abstracto: se reporta la diferencia contra los baselines en la métrica principal. Tres baselines:

1. **Ingenuo**: la predicción más simple honesta (tasa promedio). Mide qué tan difícil es el problema.
2. **Regla**: una heurística con 1-2 variables fuertes que una persona podría escribir, o la política vigente si existe. Si no existe, proponer una.
3. **Primer modelo sin tunear**: una **regresión logística sobre WoE** (referencia interpretable) y, si se van a usar árboles, un GBM con hiperparámetros por defecto.

Un modelo más complejo tiene que ganarles en el OOT por un margen que justifique perder interpretabilidad. Si la regla gana, se documenta y se discute antes de seguir.

## Experimentos como ablaciones

Cada experimento cambia **una sola cosa** respecto del líder vigente (una variable nueva, otro algoritmo, otro tratamiento de faltantes), para poder atribuir la diferencia. Cada uno queda registrado con su resultado y un veredicto (✅ aceptado, ❌ descartado, ⚠️ requiere revisión).

## Búsqueda de hiperparámetros

- La búsqueda vive dentro de train (ver árbitro intacto en `02-particiones-validacion.md`). El early stopping usa un subconjunto de train, no el conjunto con el que se va a reportar.
- **Penalizar el sobreajuste y la concentración**, no solo maximizar la métrica:
  `score = métrica_val − a · brecha(train, val) − b · exceso_de_concentración − c · participación_de_la_variable_principal`.
  Entre configuraciones con métrica casi igual, elegir la de menor sobreajuste.
- Rangos de hiperparámetros más conservadores cuanto más chico es el dataset.

## Métricas

| Métrica | Mide | Comentario |
|---|---|---|
| AUC / Gini (= 2·AUC − 1) | Capacidad de ordenar | Métrica principal de discriminación. Reportar con intervalo de confianza |
| KS | Máxima separación entre buenos y malos | Estándar en la industria; complementa al AUC |
| AUC-PR | Desempeño en la clase minoritaria | Útil con tasas de malos muy bajas |
| Brier, log-loss | Calidad de las probabilidades | Importan si el score se usa para pricing o pérdida esperada |
| Calibración por decil o por rating | PD estimada vs. observada | Obligatoria si la PD se usa como número |
| Tasa de malos por banda de score | Orden y escalonamiento | Debe ser monótona; inversiones entre bandas son una alerta |

No usar accuracy: con tasas de malos bajas no informa nada.

## Segmentación

Segmentar (un modelo por producto, canal o perfil) solo si mejora:

1. Proponer esquemas de segmentación con sentido de negocio y suficientes casos por segmento.
2. Construir un modelo rápido sin segmentar como referencia y uno rápido por segmento.
3. Adoptar la segmentación solo si mejora a la referencia en al menos 5% (lift) en el OOT.

## Calibración

- Un modelo puede ordenar bien y estar mal calibrado. Si la PD se usa en pricing, provisiones o pérdida esperada, calibrar.
- Calibrar con datos que no se usaron para entrenar (Platt o isotónica sobre un conjunto separado).
- Verificar la calibración en el OOT y por segmento. Si la tasa de malos del OOT difiere de la del desarrollo (cambio de ciclo), puede hacer falta recalibrar el nivel sin reentrenar.
- **Criterio de aceptación por rating**: la tasa de malos observada en cada rating no se aleja más de ±5 puntos de la esperada (ajustar el margen al tamaño de cada banda).
- Si el score solo se usa para ordenar o asignar ratings, decirlo explícitamente y no presentarlo como probabilidad.

## Desbalance de clases

- Con regresión logística o GBM no hace falta rebalancear para ordenar. Preferir ajustar el umbral de decisión a modificar la muestra.
- Rebalancear (sobremuestreo, `scale_pos_weight`, `is_unbalance`, pesos) **distorsiona las probabilidades**. Si después el score se usa como PD, recalibrarlo y verificar la calibración por decil. Los ratings calibrados con tasas observadas no tienen este problema.

## Escalamiento a puntos

Si el score se expresa en puntos (por ejemplo 300-850):

- Documentar el anclaje: puntos base, odds base y PDO (puntos para duplicar las odds).
- La transformación es monótona y no cambia la discriminación; solo cambia la lectura.

## Ratings y punto de corte

- La construcción de bandas de rating está en `10-ratings.md`.
- El corte es una decisión de negocio, no del modelo. Presentar para cada corte posible: tasa de aprobación, tasa de malos esperada en aprobados, volumen y, si se tiene, rentabilidad esperada. Las dos formas habituales de fijarlo son por mora máxima aceptada en la cartera o por tasa de aprobación objetivo. La elección final la toma el dueño del riesgo.
