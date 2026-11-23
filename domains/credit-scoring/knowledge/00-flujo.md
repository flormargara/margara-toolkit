# Flujo de construcción de un score

Orden de trabajo y puntos de control. No avanzar a la etapa siguiente sin cerrar el punto de control de la actual: los errores de las primeras etapas invalidan todo lo que viene después y no se corrigen con más modelado.

| # | Etapa | Punto de control (debe quedar escrito) | Detalle |
|---|---|---|---|
| 1 | Problema y uso | Decisión que el score va a tomar, población objetivo, punto de decisión en el tiempo | Abajo |
| 2 | Definición del target | Evento de default, ventana de desempeño, exclusiones, indeterminados | `01-definicion-default.md` |
| 3 | Muestra y particiones | Ventana de observación, cortes temporales de train / test / OOT | `02-particiones-validacion.md` |
| 4 | Auditoría de leakage | Lista de variables con su fecha de disponibilidad; `check_leakage.py` en verde | `03-leakage.md` |
| 5 | Features | Binning, tratamiento de faltantes, IV, monotonicidad, estabilidad por variable | `04-features.md` |
| 6 | Modelo y calibración | Baseline interpretable, comparación justa, calibración en OOT | `05-modelado-calibracion.md` |
| 7 | Sesgo de selección | Población aprobada vs. solicitantes; decisión explícita sobre reject inference | `06-sesgo-seleccion.md` |
| 8 | Validación final | Métricas en OOT por segmento, PSI, análisis de cortes y de negocio | `07-estabilidad-monitoreo.md` |
| 9 | Equidad y cumplimiento | Variables sensibles y proxies revisados | `08-equidad-regulacion.md` |
| 10 | Documentación | Ficha del modelo y checklist completos | `09-documentacion.md`, `templates/` |

## Etapa 1: problema y uso

Antes de tocar datos, responder por escrito:

- **¿Qué decisión toma el score?** Aprobar o rechazar, asignar línea, fijar tasa, priorizar cobranza. Cada una pide un target y una métrica distintos.
- **¿Sobre qué población?** Solicitantes nuevos, clientes existentes, un producto, un canal. El modelo solo vale para la población en la que se entrena.
- **¿En qué momento exacto se calcula?** El *punto de decisión* define qué información es legítima. Todo lo que ocurre después es leakage.
- **¿Qué pasa hoy sin el modelo?** La política vigente es el baseline y explica el sesgo de la muestra.
- **¿Qué costo tiene cada error?** Un falso negativo (aprobar un mal pagador) y un falso positivo (rechazar un buen pagador) casi nunca cuestan lo mismo. Esto guía el punto de corte, no el entrenamiento.

## Reglas generales

- Fijar semillas y versionar datos, código y configuración de cada corrida.
- Cada número reportado debe poder regenerarse con un comando.
- Preferir el modelo más simple que cumpla el objetivo: un score se explica a riesgo, a negocio y a un regulador.
- Las decisiones de metodología se anotan con su porqué en la ficha del modelo mientras se toman, no al final.
