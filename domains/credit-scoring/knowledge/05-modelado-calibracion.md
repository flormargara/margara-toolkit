# Modelado y calibración en crédito

Aplica todo `ml-foundations/knowledge/04-modelado.md`: spec, tres baselines, ablaciones, búsqueda dentro de train con penalización de sobreajuste y concentración, segmentación, calibración y desbalance. Acá está lo propio de crédito.

## Baseline de crédito

Entre los baselines, siempre una **regresión logística sobre WoE** (ver `04-features.md`): es la referencia interpretable y muchas veces el modelo final. La regla de baseline suele ser la política de riesgo vigente (por ejemplo, reglas de buró, ingreso mínimo y endeudamiento máximo).

## Métricas de la industria

| Métrica | Comentario |
|---|---|
| Gini (= 2·AUC − 1) | Forma habitual de reportar el AUC en riesgo |
| KS | Máxima separación entre buenos y malos; estándar en la industria |
| Tasa de malos por banda de score o rating | Debe ser monótona; inversiones entre bandas son una alerta |
| Calibración por rating | Tasa observada vs. esperada en cada rating (ver `10-ratings.md`) |

## PD y calibración

- Si la probabilidad de default se usa como número (pricing, provisiones, pérdida esperada), calibrarla y verificarla por decil y por rating en el OOT.
- **Criterio de aceptación por rating:** la tasa observada no se aleja más de ±5 puntos de la esperada (ajustar el margen al tamaño de cada banda).
- Si el modelo se rebalanceó (`scale_pos_weight`, `is_unbalance`, sobremuestreo), el score no es una PD hasta recalibrarlo. Los ratings calibrados con tasas observadas no tienen este problema.
- Si cambió el nivel de mora entre desarrollo y OOT (ciclo económico, política), recalibrar el nivel sin reentrenar puede alcanzar.

## Escalamiento a puntos

Si el score se expresa en puntos (por ejemplo 300-850):

- Documentar el anclaje: puntos base, odds base y PDO (puntos para duplicar las odds).
- La transformación es monótona y no cambia la discriminación; solo cambia la lectura.

## Punto de corte

El corte es una decisión del dueño del riesgo. Presentar para cada corte posible: tasa de aprobación, tasa de malos esperada en aprobados, volumen y, si se tiene, rentabilidad esperada. Las dos formas habituales de fijarlo:

- **Por mora máxima aceptada:** el corte que deja la tasa de malos de la cartera aprobada en el objetivo.
- **Por tasa de aprobación objetivo:** el corte que aprueba el porcentaje buscado, informando la mora resultante.

La construcción de bandas de rating está en `10-ratings.md`.
