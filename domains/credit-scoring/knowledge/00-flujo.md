# Flujo de construcción de un score

Orden de trabajo y puntos de control. No avanzar a la etapa siguiente sin cerrar el punto de control de la actual: los errores de las primeras etapas invalidan todo lo que viene después y no se corrigen con más modelado.

| # | Etapa | Punto de control (debe quedar escrito) | Detalle |
|---|---|---|---|
| 0 | Trazabilidad | La cadena evaluación → oferta → desembolso → desempeño se puede reconstruir con claves únicas | `12-trazabilidad.md` |
| 1 | Problema y uso | Decisión que el score va a tomar, población objetivo, punto de decisión, criterio de scoreabilidad | Abajo |
| 2 | Definición del target | Evento de default (con roll rate), ventana de desempeño, exclusiones, indeterminados | `01-definicion-default.md` |
| 3 | Universo y particiones | Patrón de snapshot, cortes temporales, `check_universe.py` en verde | `02-particiones-validacion.md` |
| 4 | Auditoría de leakage | Lista de variables con su fecha de disponibilidad; `check_leakage.py` en verde | `03-leakage.md` |
| 5 | Features | Faltantes, binning, IV, estabilidad por período, embudo documentado | `04-features.md` |
| 6 | Modelo y calibración | Spec, baselines, ablaciones, concentración controlada, calibración en OOT | `05-modelado-calibracion.md` |
| 7 | Sesgo de selección | Población aprobada vs. solicitantes; población de entrenamiento vs. de predicción; decisión sobre reject inference | `06-sesgo-seleccion.md` |
| 8 | Ratings | Bandas validadas en una segunda muestra; error de calibración por rating | `10-ratings.md` |
| 9 | Validación final | Métricas en OOT por segmento, PSI, análisis de cortes y de negocio | `07-estabilidad-monitoreo.md` |
| 10 | Equidad y cumplimiento | Variables sensibles y proxies revisados | `08-equidad-regulacion.md` |
| 11 | Experimento y despliegue | Grupo de control, métrica de impacto, plan de monitoreo y regla de promoción | `11-experimentacion.md`, `07-estabilidad-monitoreo.md` |
| 12 | Documentación | Ficha del modelo y checklist completos | `09-documentacion.md`, `templates/` |

## Etapa 1: problema y uso

Antes de tocar datos, responder por escrito:

- **¿Qué decisión toma el score?** Aprobar o rechazar, asignar línea, fijar tasa, priorizar cobranza. Cada una pide un target y una métrica distintos.
- **¿Sobre qué población?** Solicitantes nuevos, clientes existentes, un producto, un canal. El modelo solo vale para la población en la que se entrena.
- **¿En qué momento exacto se calcula?** El *punto de decisión* define qué información es legítima. Todo lo que ocurre después es leakage.
- **¿Qué pasa hoy sin el modelo?** La política vigente es el baseline y explica el sesgo de la muestra.
- **¿Qué costo tiene cada error?** Un falso negativo (aprobar un mal pagador) y un falso positivo (rechazar un buen pagador) casi nunca cuestan lo mismo. Esto guía el punto de corte, no el entrenamiento.
- **¿A quién no se va a scorear?** Criterio mínimo de scoreabilidad y exclusiones por política (ver `06-sesgo-seleccion.md`).
- **¿Cómo se va a medir el impacto?** Si no hay forma de comparar contra un grupo de control o contra la política vigente, definirla antes de construir (ver `11-experimentacion.md`).

Empezar por las preguntas, no por los datos: los datos reflejan el pasado y el modelo se usa para decidir el futuro.

## Reglas generales

- Fijar semillas y versionar datos, código y configuración de cada corrida.
- Cada número reportado debe poder regenerarse con un comando.
- Preferir el modelo más simple que cumpla el objetivo: un score se explica a riesgo, a negocio y a un regulador.
- Las decisiones de metodología se anotan con su porqué en la ficha del modelo mientras se toman, no al final.
