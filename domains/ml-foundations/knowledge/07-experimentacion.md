# Experimentación y medición de impacto

Una buena métrica offline no prueba que el modelo genere valor. El impacto se mide comparando contra lo que habría pasado sin el modelo, y eso requiere un grupo de control diseñado antes de lanzar.

## Diseño del grupo de control

- **Aleatorio dentro de cada grupo o banda de predicción**, no global: así se puede medir el efecto por segmento y el control representa a toda la población.
- **Tamaño por banda** según el costo de no actuar y lo que haga falta medir. Si el modelo se reentrena con el control, el tamaño también tiene que alcanzar para entrenar.
- **Tamaño mínimo para medir:** `control mínimo = eventos objetivo / tasa esperada del evento`, por banda. Si no alcanza, alargar el período o agrupar bandas.
- **Exclusiones del control** por riesgo o por regulación, documentadas y con su volumen.
- **Asignación determinista y reproducible** (hash del identificador con una semilla registrada).
- Documentar qué recibe exactamente el control (nada, el proceso anterior, un mínimo obligatorio).

## Control persistente entre corridas

Si el modelo se corre todos los días o todos los meses, reasignar el control desde cero en cada corrida lo contamina: una entidad que fue control y después tratada ya no sirve para ninguna de las dos mediciones.

Asignación persistente ("sticky"), por banda:

1. Quien fue control sigue siendo control (para el conteo manda la banda nueva).
2. Si falta para llegar al tamaño objetivo, se completa primero con entidades **nuevas**, que no estaban en la corrida anterior.
3. Solo si todavía falta, se completa con ex-tratados.
4. Se registra la variante, la corrida y la versión del modelo en cada asignación.

## Medición

- **Intención de tratamiento (ITT):** se compara a todos los asignados a tratamiento contra todos los asignados a control, aunque algunos tratados no hayan recibido la acción. Es la estimación honesta del efecto de usar el modelo.
- Separar dos preguntas que suelen mezclarse:
  - **¿El modelo ordena?** Métrica de discriminación **sobre el grupo de control**, donde el resultado no está afectado por la acción.
  - **¿La acción guiada por el modelo funciona?** Diferencia de resultados entre tratamiento y control (uplift), por banda.
- No nombrar "poder discriminante" a un cociente entre control y tratamiento: eso mide impacto.
- Reportar el impacto también en términos de negocio: valor generado, costo de la acción, volumen.

## Métricas de negocio desde el diseño

Las métricas de ML (AUC, KS, error) dicen si el modelo ordena o acierta; las de negocio, si la decisión que toma mejora algo. Se definen por separado y antes de construir, no se deducen al final de las de ML.

- **Cada banda o etiqueta tiene su accionable:** qué se hace con quien cae ahí (aprobar con límite alto, llamar en 48 horas, no contactar). Una banda sin acción asociada no necesita existir, y un corte que no cambia ninguna acción no se discute.
- Para cada accionable: la métrica de negocio que mueve (tasa de recupero, pérdida, conversión, costo por gestión), su unidad y la dirección deseada.
- Los tableros muestran las dos familias en secciones separadas: que mejore el AUC no dice que mejore el negocio, y al revés.

| Banda | Accionable | Métrica de negocio | Dirección |
|---|---|---|---|
| Alto riesgo | Gestión temprana por teléfono | Tasa de regularización a 30 días | ↑ |
| Riesgo medio | Recordatorio digital | Costo por cuenta regularizada | ↓ |
| Bajo riesgo | Sin gestión (autocura) | Tasa de autocura | se mantiene |

## Ficha de impacto

La performance técnica no dice cuánto valor genera el modelo. Cada implementación (dónde y cómo se usa el modelo) tiene una ficha de impacto (`templates/ficha-impacto.md`), armada en cinco capas:

1. **Objetivo:** objetivo de negocio, KPI nativo del dominio con su unidad y la dirección deseada (sube o baja). No se convierten todas las unidades a una sola.
2. **Cálculo propuesto:** cómo se calcula el KPI y su contrafactual, con las tablas, los supuestos y un valor de muestra.
3. **Elección:** se fija el cálculo, el tipo de contrafactual y la ventana de maduración.
4. **Cálculo versionado:** código con parámetros estándar (período, identificadores) e inmutable. Cambiarlo genera una versión nueva.
5. **Aprobación:** el dueño del dominio aprueba esa versión. Solo las fichas aprobadas entran a los números oficiales; las demás corren en modo ensayo.

### Tipos de contrafactual

| Contrafactual | Lectura |
|---|---|
| Grupo de control u holdout | El más confiable; requiere diseñarlo antes de lanzar |
| A/B | Igual, cuando se comparan dos variantes |
| Champion-challenger | Impacto relativo al modelo anterior, no al proceso sin modelo |
| Línea base (antes/después) | Confunde el efecto del modelo con todo lo demás que cambió; usar con cautela |
| Sin contrafactual | Solo el resultado absoluto. Se registra marcado así y abre un pendiente para diseñar un holdout. No se presenta como impacto |

### Reglas de registro

- **Ventana de maduración:** mientras el resultado no se estabiliza (mora, contracargos, recompras), la medición es **preliminar** y se recalcula en cada cierre hasta quedar **definitiva**.
- **Append-only:** un recálculo agrega una revisión nueva, nunca pisa la anterior. Una vista aparte muestra la revisión vigente.
- **"Sin dato" no es "impacto cero":** un período sin datos se registra como tal, con su motivo.
- Cada valor queda atribuido a la versión del modelo vigente en ese período.
- Contrato de salida por período: valor observado, valor contrafactual, impacto, tamaño (n), intervalo si se puede, y advertencias.
- Repetir un cierre con los mismos datos no genera revisiones duplicadas; si un cálculo falla, se registra la falla y el resto sigue.

## Pilotos y pruebas

- Antes del despliegue completo, un **backtest** sobre el período anterior con el dataset congelado, revisado con el negocio, y un **piloto** con muestreo estratificado y monitoreo diario de los primeros días.
- Para validar un cambio de umbral o de alcance, una **prueba controlada** sobre una muestra acotada de la zona nueva es la única evidencia directa (ver `05-poblacion-y-sesgo.md`).
- Experimentar también sobre la política o la acción, no solo sobre el modelo: probar dos o tres estrategias contra un control.
- Si hay muchas acciones posibles y se aprende sobre la marcha, evaluar enfoques secuenciales (bandits) en lugar de pruebas A/B fijas.
