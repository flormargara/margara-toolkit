# Checklist de validación — [nombre del modelo] v[versión]

Marcar cada punto. Si un punto no aplica o no se cumple, dejarlo sin marcar y escribir la excepción con su justificación debajo.

## Problema y target
- [ ] Decisión, población y punto de decisión escritos
- [ ] Evento de default, ventana de desempeño y regla de peor estado definidos y acordados con riesgo
- [ ] Ventana de desempeño justificada con curvas de maduración
- [ ] Indeterminados y exclusiones documentados con su volumen
- [ ] Sin cohortes inmaduras en ninguna partición
- [ ] Cantidad de malos suficiente para la complejidad del modelo

## Particiones
- [ ] Validación final out-of-time
- [ ] Split por persona / grupo (sin la misma unidad en dos particiones)
- [ ] Transformaciones (binning, WoE, imputación, escalado, selección) ajustadas solo con train
- [ ] OOT mirado una sola vez, al final

## Leakage
- [ ] Diccionario de variables con fecha de disponibilidad de cada una
- [ ] `check_leakage.py --features` en verde sobre la lista final
- [ ] Las 10 variables más importantes revisadas una por una
- [ ] Ninguna variable con IV > 0.5 sin explicación
- [ ] Variables verificadas contra una muestra de producción

## Features y modelo
- [ ] Binning con tamaño mínimo y monotonicidad (o excepción justificada)
- [ ] Estabilidad por variable (CSI) entre cohortes de desarrollo
- [ ] Colinealidad controlada; signos de coeficientes consistentes
- [ ] Baseline de regresión logística construido
- [ ] Modelo final comparado contra el baseline con las mismas particiones

## Desempeño (en OOT)
- [ ] AUC/Gini y KS con intervalo de confianza
- [ ] Métricas por cohorte mensual y por segmento
- [ ] Tasa de malos monótona por banda de score
- [ ] Calibración por decil (si la PD se usa como número)
- [ ] PSI del score desarrollo vs. OOT

## Sesgo de selección y equidad
- [ ] Población aprobada vs. solicitantes comparada; limitación documentada
- [ ] Decisión sobre reject inference tomada y justificada
- [ ] Sin variables sensibles; proxies revisados
- [ ] Métricas por grupo (si hay datos para auditar)
- [ ] Reason codes disponibles y comprensibles

## Producción
- [ ] Todas las variables existen en producción con la misma definición
- [ ] Plan de monitoreo con métricas, frecuencia, umbrales y responsable
- [ ] Análisis de punto de corte entregado al dueño del riesgo
- [ ] Ficha del modelo completa
- [ ] Resultados reproducibles con un comando

## Excepciones

| Punto | Motivo | Mitigación |
|---|---|---|
| | | |
