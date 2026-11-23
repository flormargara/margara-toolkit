# Modelado y calibración

## Baseline primero

Siempre construir primero una **regresión logística sobre WoE**. Es el punto de comparación y muchas veces el modelo final. Un modelo más complejo (GBM, por ejemplo) tiene que ganarle en el OOT por un margen que justifique perder interpretabilidad, y la comparación se hace con las mismas particiones y las mismas variables candidatas.

## Métricas

| Métrica | Mide | Comentario |
|---|---|---|
| AUC / Gini (= 2·AUC − 1) | Capacidad de ordenar | Métrica principal de discriminación. Reportar con intervalo de confianza |
| KS | Máxima separación entre buenos y malos | Estándar en la industria; complementa al AUC |
| Brier, log-loss | Calidad de las probabilidades | Importan si el score se usa para pricing o pérdida esperada |
| Calibración por decil | PD estimada vs. observada | Obligatoria si la PD se usa como número, no solo para ordenar |
| Tasa de malos por banda de score | Orden y escalonamiento | Debe ser monótona; inversiones entre bandas son una alerta |

No usar accuracy: con tasas de malos bajas no informa nada.

## Calibración

- Un modelo puede ordenar bien y estar mal calibrado. Si la PD se usa en pricing, provisiones o pérdida esperada, calibrar.
- Calibrar con datos que no se usaron para entrenar (Platt o isotónica sobre un conjunto separado).
- Verificar la calibración en el OOT y por segmento. Si la tasa de malos del OOT difiere de la del desarrollo (cambio de ciclo), puede hacer falta recalibrar el nivel (intercepto) sin reentrenar.
- Reportar gráfico de PD media estimada vs. tasa de malos observada por decil.

## Escalamiento a puntos

Si el score se expresa en puntos (por ejemplo 300-850):

- Documentar el anclaje: puntos base, odds base y PDO (puntos para duplicar las odds).
- La transformación es monótona y no cambia la discriminación; solo cambia la lectura.

## Punto de corte

El corte es una decisión de negocio, no del modelo. Presentar para cada corte posible: tasa de aprobación, tasa de malos esperada en aprobados, volumen y, si se tiene, rentabilidad esperada. La elección final la toma el dueño del riesgo.

## Desbalance de clases

- Con regresión logística no hace falta rebalancear para ordenar. Si se rebalancea (sobremuestreo, pesos), las probabilidades quedan sesgadas y hay que corregirlas.
- Preferir ajustar el umbral de decisión a modificar la muestra.
