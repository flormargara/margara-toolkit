# Flujo de un proyecto de ML supervisado

Prácticas para modelos que predicen un evento o un valor futuro a partir de datos históricos: clasificación, regresión o ranking, con datos que cambian en el tiempo. Cada dominio (por ejemplo `credit-scoring`) agrega lo específico sobre esta base.

Fuera de alcance: pronóstico de series (horizonte, estacionalidad, variables exógenas) y optimización (asignación, ruteo). La optimización no se valida con train y test sino contra resultados históricos o escenarios reservados.

No avanzar a la etapa siguiente sin cerrar el punto de control de la actual: los errores de las primeras etapas invalidan todo lo que viene después y no se corrigen con más modelado.

| # | Etapa | Punto de control (debe quedar escrito) | Detalle |
|---|---|---|---|
| 0 | Trazabilidad | Se puede reconstruir predicción → decisión → resultado para el período a usar; `check_traceability.py` con la cobertura de cada salto | `08-trazabilidad.md` |
| 1 | Problem framing | Hace falta ML; decisión, población, momento de la predicción, demora hasta la acción, costo de cada error, uso y fallback, forma de medir el impacto | Abajo |
| 2 | Universo y particiones | Target perfilado por período (`target_profile.py`), grano, horizonte, esquema temporal; `check_universe.py` en verde | `01-universo-particiones.md` |
| 3 | Leakage | Variables con su fecha de disponibilidad; `check_leakage.py` en verde | `02-leakage.md` |
| 4 | Features | Ideas ancladas a fuentes verificadas y handoff (`templates/feature-handoff.md`); faltantes, estabilidad por período, embudo de selección documentado separando selección sin target y predictiva | `03-features.md` |
| 5 | Dataset | Una receta para train, validación y scoring; `check_dataset.py` en verde; contrato del dataset | `03b-dataset.md` |
| 6 | Modelado | Spec, baselines, leaderboard con ablaciones, búsqueda dentro de train, incertidumbre de cada métrica, calibración; `check_concentration.py` en verde | `04-modelado.md` |
| 7 | Población | Población de entrenamiento vs. de predicción comparada; sesgo de selección documentado | `05-poblacion-y-sesgo.md` |
| 8 | Experimento e impacto | Grupo de control, ficha de impacto, piloto | `07-experimentacion.md` |
| 9 | Monitoreo | Tres capas, referencia correcta, gate de entradas (`check_inputs.py`), umbrales, responsables, regla de promoción (`promotion.py`) | `06-monitoreo.md` |
| 10 | Documentación y producción | Ficha del modelo y checklist completos; documentación verificada contra el código; set de entrenamiento guardado y contrato entre pasos verificado antes de desplegar | `09-documentacion.md`, `templates/` |

## ¿Hace falta ML?

Antes del problem framing, tres preguntas (`templates/discovery.md` las junta con el resto del discovery). Si alguna da "no", el proyecto es otro:

1. **¿Hay una decisión periódica y repetible que dependa de información disponible?** Si es un análisis puntual, alcanza con analítica o un tablero.
2. **¿Una regla simple ya captura el valor?** Construir la regla (el baseline "regla" de `04-modelado.md`) y estimar cuánto valor agregaría un modelo sobre ella. Mirar el valor, no la cobertura: el resto que la regla no cubre puede concentrar la pérdida. Si la ganancia esperada no paga construir y mantener el modelo, quedarse con la regla y monitorearla.
3. **¿Hay un target histórico con calidad razonable?** Si no, primero instrumentar la captura y la trazabilidad (`08-trazabilidad.md`), y documentar los criterios con los que se decide hoy.

## Problem framing

Empezar por las preguntas, no por los datos: los datos reflejan el pasado y el modelo se usa para decidir el futuro. Responder por escrito antes de tocar datos:

- **¿Qué decisión apoya el modelo?** Priorizar, aprobar, asignar, recomendar, estimar. Cada decisión pide un target y una métrica distintos.
- **¿Sobre qué población?** El modelo solo vale para la población en la que se entrena. Si la población de predicción es otra, ver `05-poblacion-y-sesgo.md`.
- **¿En qué momento exacto se predice?** Ese momento define qué información es legítima. Todo lo que ocurre después es leakage.
- **¿Cuánto tarda la acción después de la predicción?** Si pasan días entre predecir y actuar (armar una campaña, asignar un caso), el target se mide desde que se puede actuar (ver `01-universo-particiones.md`).
- **¿Qué pasa hoy sin el modelo?** La regla o el proceso vigente es el baseline y explica el sesgo de la muestra.
- **¿Qué cuesta cada error?** Falsos positivos y falsos negativos casi nunca cuestan lo mismo. Esto guía la métrica principal y el umbral de decisión.
- **¿Cómo se va a medir el impacto?** Si no hay forma de comparar contra un grupo de control o contra el proceso vigente, definirla antes de construir (`07-experimentacion.md`).
- **¿A quién no se va a predecir?** Casos sin información suficiente o fuera del alcance, con su volumen.

### Uso del modelo

- **Quién consume la salida y qué sistema o proceso la toma.**
- **Frecuencia, latencia y modo de entrega** (batch, API, tabla, archivo), acordados con el consumidor junto con el formato de salida.
- **Qué pasa si el modelo falla o no está disponible:** regla de respaldo, versión anterior, o no decidir. Si el sistema opera abierto (sigue sin el modelo) o cerrado (se detiene).
- **Quién mantiene el modelo** en cada tramo del flujo (datos, pipeline, integración, monitoreo). Un modelo sin responsable de mantenimiento queda huérfano.

### Señales de alarma

Detenerse y resolverlas antes de seguir:

- El problema no tiene números (magnitud, evolución, costo).
- La hipótesis es "juicio experto" y nadie está dispuesto a contrastarla con datos.
- No hay proceso actual, responsables ni registros de cómo se decide hoy.
- El proyecto no tiene sponsor con poder de decisión o no aparece en los objetivos del área.
- El stakeholder no logra elegir una sola métrica de éxito.

### Estado de cada afirmación

El framing evoluciona con la evidencia. Marcar cada afirmación con su estado: **explícita** (lo dice el pedido), **candidata** (lectura propuesta, sin confirmar), **confirmada**, **desconocida** o **contradicha**. No inventar lo que el pedido no sostiene: un campo sin respaldo queda como desconocido.

El framing es **usable** cuando el problema, la decisión y el resultado de negocio están confirmados, las contradicciones están a la vista y hay una siguiente actividad que puede producir evidencia. Target, horizonte, validación y algoritmo pueden quedar abiertos a propósito: se definen en las etapas siguientes.

El target se elige por la decisión que apoya, no porque sea el que mejor se predice. Entre opciones igualmente útiles, recién ahí la predictibilidad desempata.

## Reglas generales

- Fijar semillas y versionar datos, código, configuración y artefactos de cada corrida.
- Cada número reportado indica de qué partición sale, cuánto podría moverse y puede regenerarse con un comando.
- Preferir el modelo más simple que cumpla el objetivo.
- Las decisiones de metodología se anotan con su porqué mientras se toman, no al final.
- Una etapa no se cierra porque un script terminó bien o la métrica es buena: eso es evidencia. Se cierra con una decisión explícita del responsable (aceptar, aceptar con condiciones, devolver o descartar).
