# Flujo de construcción de un score

Un score de riesgo crediticio es un modelo de ML supervisado: aplica todo `ml-foundations/knowledge/` y además lo específico de crédito que está en este dominio. Para cada etapa, leer primero el archivo general y después el de crédito.

No avanzar a la etapa siguiente sin cerrar el punto de control de la actual.

| # | Etapa | Punto de control | General | Específico de crédito |
|---|---|---|---|---|
| 0 | Trazabilidad | La cadena evaluación → oferta → desembolso → desempeño se puede reconstruir | `ml-foundations/knowledge/08-trazabilidad.md` | `12-trazabilidad.md` |
| 1 | Problema y uso | Decisión, población, punto de decisión, scoreabilidad, forma de medir el impacto | `ml-foundations/knowledge/00-flujo.md` | Abajo |
| 2 | Target | Evento de default (con roll rate), ventana de desempeño, exclusiones, indeterminados | — | `01-definicion-default.md` |
| 3 | Universo y particiones | Patrón de snapshot, cortes temporales, `check_universe.py` en verde | `ml-foundations/knowledge/01-universo-particiones.md` | `02-particiones-validacion.md` |
| 4 | Leakage | Variables con fecha de disponibilidad; `check_leakage.py` en verde con la lista de crédito | `ml-foundations/knowledge/02-leakage.md` | `03-leakage.md` |
| 5 | Features | Faltantes, estabilidad por período, WoE/IV, embudo | `ml-foundations/knowledge/03-features.md` | `04-features.md` |
| 6 | Modelo y calibración | Spec, baselines (incluida logística sobre WoE), ablaciones, calibración de la PD | `ml-foundations/knowledge/04-modelado.md` | `05-modelado-calibracion.md` |
| 7 | Sesgo de selección | Aprobados vs. solicitantes; reject inference; población de entrenamiento vs. de predicción | `ml-foundations/knowledge/05-poblacion-y-sesgo.md` | `06-sesgo-seleccion.md` |
| 8 | Ratings | Bandas validadas en una segunda muestra; error de calibración por rating | — | `10-ratings.md` |
| 9 | Validación final y monitoreo | Métricas en OOT por cohorte de originación, PSI, plan de monitoreo, regla de promoción | `ml-foundations/knowledge/06-monitoreo.md` | `07-estabilidad-monitoreo.md` |
| 10 | Equidad y cumplimiento | Variables sensibles y proxies revisados; reason codes | — | `08-equidad-regulacion.md` |
| 11 | Experimento | Grupo de control o banda de prueba, métrica de impacto | `ml-foundations/knowledge/07-experimentacion.md` | `11-experimentacion.md` |
| 12 | Documentación | Ficha del modelo y checklist de crédito completos | `ml-foundations/knowledge/09-documentacion.md` | `09-documentacion.md`, `templates/` |

## Etapa 1: problema y uso en crédito

Además del problem framing general, responder por escrito:

- **¿Qué decisión toma el score?** Aprobar o rechazar, asignar línea, fijar tasa, aumentar o reducir límite, priorizar cobranza. Cada una pide un target y una métrica distintos (para cobranza, ver el dominio `collections`).
- **¿Sobre qué población?** Solicitantes nuevos, clientes existentes, reactivaciones, un producto, un canal.
- **¿En qué momento exacto se calcula?** La fecha de la solicitud o de la evaluación define qué información de buró y de comportamiento es legítima.
- **¿Qué hace hoy la política de riesgo sin el modelo?** Es el baseline y explica el sesgo de la muestra de aprobados.
- **¿Qué cuesta cada error?** Aprobar un mal pagador (pérdida) y rechazar un buen pagador (negocio perdido) casi nunca cuestan lo mismo. Esto guía el punto de corte, no el entrenamiento.
- **¿A quién no se va a scorear?** Criterio mínimo de scoreabilidad y exclusiones por política (ver `06-sesgo-seleccion.md`).

## Tipos de score habituales

| Score | Cuándo se calcula | Datos típicos |
|---|---|---|
| Originación (onboarding) | En la solicitud | Buró, datos de la solicitud, relación previa con la entidad |
| New to credit | En la solicitud, sin historial crediticio | Datos alternativos: transaccionales, de otras empresas del grupo, dispositivo |
| Comportamental | Periódicamente sobre la cartera | Uso y pago de los productos propios, buró |
| Upsell / downsell | Periódicamente sobre la cartera activa | Comportamental más capacidad estimada (por ejemplo, ingresos) |
| Cobranzas | Al entrar en mora | Ver el dominio `collections` |
