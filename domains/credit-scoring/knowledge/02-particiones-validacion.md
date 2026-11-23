# Universo y particiones en crédito

Aplica todo `ml-foundations/knowledge/01-universo-particiones.md`: validación out-of-time obligatoria, patrón de snapshot, elegibilidad idéntica, cinco chequeos de integridad (`check_universe.py`), árbitro intacto y sampling solo en train. Acá está lo específico de crédito.

## Fecha de corte y horizonte

- La `fecha_corte` es la fecha de la solicitud o evaluación (originación) o la fecha de observación de la cartera (comportamental).
- El horizonte es la **ventana de desempeño** definida en `01-definicion-default.md` (por ejemplo 12 meses). La madurez se impone en la query: el último corte usable es `último dato de desempeño completo − ventana`.
- Para scores comportamentales con observaciones mensuales, la misma cuenta aparece en muchos cortes: split por cuenta o persona, o una fila por persona con hash determinista.

## Esquema típico

```
|---- desarrollo (train + test) ----|-- gap --|---- OOT ----|
   originaciones de 18-24 meses      1-3 meses   últimos meses maduros
```

- Elegir los puntos de observación para que capturen suficientes malos, cubran la estacionalidad y sean representativos de la cartera actual y lo más recientes posible.
- Si hubo cambios de política o de producto en el período, que el OOT quede después del cambio: es el régimen en el que va a operar el modelo.

## Qué reportar además de lo general

- Métricas por cohorte de originación del OOT, no solo el agregado.
- Métricas por segmento: producto, canal, cliente nuevo vs. existente, con y sin historial en buró.
- Tasa de malos por cohorte en cada partición, para que se vea si el OOT tiene un nivel de riesgo distinto.
