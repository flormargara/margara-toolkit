# Checklist de validación — [nombre del modelo] v[versión]

Marcar cada punto. Si un punto no aplica o no se cumple, dejarlo sin marcar y escribir la excepción con su justificación al final.

## Trazabilidad y problem framing
- [ ] Cobertura de cada salto predicción → decisión → resultado medida para el período del universo
- [ ] Justificado que hace falta ML (comparado contra una regla por valor, no por cobertura)
- [ ] Decisión, población, momento de la predicción, demora hasta la acción y población excluida escritos
- [ ] Consumidor, modo de entrega, respaldo ante fallas y responsable de mantenimiento acordados
- [ ] Costo de cada tipo de error y forma de medir el impacto definidos
- [ ] Target elegido por la decisión que apoya

## Universo y particiones
- [ ] Target perfilado por período; `target_profile.py` viable o rango viable justificado
- [ ] Validación final fuera de tiempo (si hay estructura temporal)
- [ ] Validación final reportada completa y sin entidades vistas; árbitro elegido antes de mirar resultados
- [ ] Test rotulado como conjunto de selección si se usó para elegir
- [ ] Elegibilidad idéntica en train, validación y predicción
- [ ] `check_universe.py` en verde (orden, horizonte, madurez, entidades, duplicados)
- [ ] Ninguna entidad en dos particiones de la búsqueda (train, test, folds)
- [ ] Transformaciones y sampling ajustados solo con train
- [ ] Early stopping y búsqueda sin usar el conjunto del veredicto
- [ ] Validación final mirada una sola vez

## Leakage
- [ ] Diccionario de variables con fecha de disponibilidad
- [ ] `check_leakage.py` en verde sobre la lista final
- [ ] Las 10 variables más importantes revisadas una por una
- [ ] Variables verificadas contra una muestra de producción

## Features y modelo
- [ ] Semántica de faltantes, capping y población mínima definidas
- [ ] Estabilidad por período (nulos, distribución, relación con el target sin inversión)
- [ ] Embudo de variables documentado con conteos, separando selección sin target y predictiva
- [ ] Selección predictiva solo dentro de train
- [ ] Dataset de una sola receta para train, validación y scoring; `check_dataset.py` en verde y contrato escrito
- [ ] Leaderboard completo, con linaje y sin filas borradas, dentro de una sola versión del dataset
- [ ] Antes de tunear, diagnóstico escrito (brecha vs. techo); estudio corto antes que largo
- [ ] Spec escrita (métrica principal, "suficientemente bueno", restricciones)
- [ ] Baselines construidos: ingenuo, regla y modelo sin tunear
- [ ] Experimentos registrados como ablaciones con veredicto
- [ ] `check_concentration.py` en verde (o concentración justificada)
- [ ] Segmentación adoptada solo si mejora al modelo único
- [ ] Si hubo rebalanceo y la probabilidad se usa como número: recalibrado
- [ ] Población de entrenamiento vs. de predicción comparada

## Desempeño
- [ ] Métrica principal con intervalo de confianza en la validación final; diferencias menores que la dispersión tratadas como empate
- [ ] Métricas por período y por segmento
- [ ] Calibración verificada (si la predicción se usa como número)
- [ ] PSI de la predicción desarrollo vs. validación

## Producción
- [ ] Todas las variables existen en producción con la misma definición
- [ ] Se registra la predicción para toda la población, incluida la excluida por reglas
- [ ] Cada predicción guarda versión del modelo y de la regla o campaña
- [ ] Grupo de control diseñado si la acción cambia el resultado
- [ ] Monitoreo en tres capas con umbrales y responsable
- [ ] Monitoreo referido a la validación final de la versión vigente y a los artefactos del modelo vigente
- [ ] Gate de entradas (esquema, volumen, frescura) antes de cada corrida, con falla cerrada
- [ ] Ficha de impacto con contrafactual y ventana de maduración
- [ ] Regla de promoción con margen mínimo definida
- [ ] Artefactos con tag inmutable
- [ ] Documentación verificada contra el código
- [ ] Ficha del modelo completa

## Excepciones

| Punto | Alcance | Motivo | Mitigación | Responsable | Vence o se revisa |
|---|---|---|---|---|---|
| | | | | | |
