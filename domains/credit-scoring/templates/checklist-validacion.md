# Checklist de validación — [nombre del modelo] v[versión]

> Versión de crédito de la plantilla genérica de `ml-foundations/templates/`. Incluye todos sus puntos más los específicos de riesgo crediticio.

Marcar cada punto. Si un punto no aplica o no se cumple, dejarlo sin marcar y escribir la excepción con su justificación debajo.

## Trazabilidad
- [ ] Cobertura de cada salto evaluación → oferta → desembolso → desempeño medida para el período del universo
- [ ] Limitaciones de trazabilidad documentadas en la ficha

## Problema y target
- [ ] Decisión, población, punto de decisión y criterio de scoreabilidad escritos
- [ ] Forma de medir el impacto definida (grupo de control o comparación contra la política vigente)
- [ ] Evento de default justificado con análisis de roll rate
- [ ] Evento de default, ventana de desempeño y regla de peor estado definidos y acordados con riesgo
- [ ] Tratamiento de refinanciaciones, reestructuraciones y renovaciones definido
- [ ] Umbral de monto mínimo para "malo" definido (o justificado que no hace falta)
- [ ] Ventana de desempeño justificada con curvas de maduración
- [ ] Indeterminados y exclusiones documentados con su volumen
- [ ] Sin cohortes inmaduras en ninguna partición
- [ ] Cantidad de malos suficiente para la complejidad del modelo

## Universo y particiones
- [ ] Validación final out-of-time
- [ ] Elegibilidad idéntica en train, validación y scoring
- [ ] `check_universe.py` en verde (orden, horizonte, madurez, entidades, duplicados)
- [ ] Split por persona / grupo (sin la misma unidad en dos particiones de la búsqueda); validación final reportada completa y sin personas vistas
- [ ] Transformaciones (binning, WoE, imputación, escalado, selección) y sampling ajustados solo con train
- [ ] Early stopping y búsqueda de hiperparámetros sin usar el conjunto del veredicto
- [ ] OOT mirado una sola vez, al final

## Leakage
- [ ] Diccionario de variables con fecha de disponibilidad de cada una
- [ ] `check_leakage.py --features` en verde sobre la lista final
- [ ] Las 10 variables más importantes revisadas una por una
- [ ] Ninguna variable con IV > 0.5 sin explicación
- [ ] Variables verificadas contra una muestra de producción

## Features y modelo
- [ ] Semántica de faltantes, capping y población mínima definidas por variable
- [ ] Binning con tamaño mínimo y monotonicidad (o excepción justificada)
- [ ] Estabilidad por período (nulos, distribución, IV en rango, relación con el target sin inversión)
- [ ] Embudo de variables documentado con conteos
- [ ] Colinealidad controlada; signos de coeficientes consistentes
- [ ] Spec del modelo escrita (métrica principal, criterio de "suficientemente bueno", restricciones)
- [ ] Baselines construidos: ingenuo, regla y modelo sin tunear (incluida regresión logística)
- [ ] Modelo final comparado contra los baselines con las mismas particiones
- [ ] `check_concentration.py` en verde (o concentración justificada)
- [ ] Segmentación adoptada solo si mejora al modelo único en al menos 5%
- [ ] Si hubo rebalanceo y el score se usa como probabilidad: recalibrado
- [ ] Población de entrenamiento vs. de predicción comparada (validación adversarial si difieren)

## Ratings
- [ ] Bandas monótonas, con participación mínima y tasas distinguibles
- [ ] Cortes verificados en una segunda muestra y estresados
- [ ] Error de calibración por rating dentro del margen acordado

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
- [ ] Se registra el score de todos los solicitantes, incluidos los rechazados por reglas
- [ ] Cada evaluación guarda versión del modelo y versión de la política o campaña
- [ ] Grupo de control diseñado (por rating, persistente, tamaño mínimo) si la acción cambia el resultado
- [ ] Plan de monitoreo en tres capas (negocio, modelo, datos) con métricas, frecuencia, umbrales y responsable
- [ ] Regla de promoción champion / challenger / recalibrado con margen mínimo definida
- [ ] Artefactos y corridas con tag inmutable
- [ ] Documentación verificada contra el código
- [ ] Análisis de punto de corte entregado al dueño del riesgo
- [ ] Ficha del modelo completa
- [ ] Resultados reproducibles con un comando

## Excepciones

| Punto | Alcance | Motivo | Mitigación | Responsable | Vence o se revisa |
|---|---|---|---|---|---|
| | | | | | |
