# Flujo de un proyecto de ML supervisado

Prácticas para modelos que predicen un evento o un valor futuro a partir de datos históricos: clasificación, regresión o ranking, con datos que cambian en el tiempo. Cada dominio (por ejemplo `credit-scoring`) agrega lo específico sobre esta base.

No avanzar a la etapa siguiente sin cerrar el punto de control de la actual: los errores de las primeras etapas invalidan todo lo que viene después y no se corrigen con más modelado.

| # | Etapa | Punto de control (debe quedar escrito) | Detalle |
|---|---|---|---|
| 0 | Trazabilidad | Se puede reconstruir predicción → decisión → resultado para el período a usar | `08-trazabilidad.md` |
| 1 | Problem framing | Decisión, población, momento de la predicción, costo de cada error, forma de medir el impacto | Abajo |
| 2 | Universo y particiones | Target, grano, horizonte, esquema temporal; `check_universe.py` en verde | `01-universo-particiones.md` |
| 3 | Leakage | Variables con su fecha de disponibilidad; `check_leakage.py` en verde | `02-leakage.md` |
| 4 | Features | Faltantes, estabilidad por período, embudo de selección documentado | `03-features.md` |
| 5 | Modelado | Spec, baselines, ablaciones, búsqueda dentro de train, calibración; `check_concentration.py` en verde | `04-modelado.md` |
| 6 | Población | Población de entrenamiento vs. de predicción comparada; sesgo de selección documentado | `05-poblacion-y-sesgo.md` |
| 7 | Experimento y despliegue | Grupo de control, métrica de impacto, piloto | `07-experimentacion.md` |
| 8 | Monitoreo | Tres capas, umbrales, responsables, regla de promoción | `06-monitoreo.md` |
| 9 | Documentación | Ficha del modelo y checklist completos; documentación verificada contra el código | `09-documentacion.md`, `templates/` |

## Problem framing

Empezar por las preguntas, no por los datos: los datos reflejan el pasado y el modelo se usa para decidir el futuro. Responder por escrito antes de tocar datos:

- **¿Qué decisión apoya el modelo?** Priorizar, aprobar, asignar, recomendar, estimar. Cada decisión pide un target y una métrica distintos.
- **¿Sobre qué población?** El modelo solo vale para la población en la que se entrena. Si la población de predicción es otra, ver `05-poblacion-y-sesgo.md`.
- **¿En qué momento exacto se predice?** Ese momento define qué información es legítima. Todo lo que ocurre después es leakage.
- **¿Qué pasa hoy sin el modelo?** La regla o el proceso vigente es el baseline y explica el sesgo de la muestra.
- **¿Qué cuesta cada error?** Falsos positivos y falsos negativos casi nunca cuestan lo mismo. Esto guía la métrica principal y el umbral de decisión.
- **¿Cómo se va a medir el impacto?** Si no hay forma de comparar contra un grupo de control o contra el proceso vigente, definirla antes de construir.
- **¿A quién no se va a predecir?** Casos sin información suficiente o fuera del alcance, con su volumen.

El target se elige por la decisión que apoya, no porque sea el que mejor se predice. Entre opciones igualmente útiles, recién ahí la predictibilidad desempata.

## Reglas generales

- Fijar semillas y versionar datos, código, configuración y artefactos de cada corrida.
- Cada número reportado indica de qué partición sale y puede regenerarse con un comando.
- Preferir el modelo más simple que cumpla el objetivo.
- Las decisiones de metodología se anotan con su porqué mientras se toman, no al final.
