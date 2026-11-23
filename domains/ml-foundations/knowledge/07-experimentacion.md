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

## Pilotos y pruebas

- Antes del despliegue completo, un **backtest** sobre el período anterior con el dataset congelado, revisado con el negocio, y un **piloto** con muestreo estratificado y monitoreo diario de los primeros días.
- Para validar un cambio de umbral o de alcance, una **prueba controlada** sobre una muestra acotada de la zona nueva es la única evidencia directa (ver `05-poblacion-y-sesgo.md`).
- Experimentar también sobre la política o la acción, no solo sobre el modelo: probar dos o tres estrategias contra un control.
- Si hay muchas acciones posibles y se aprende sobre la marcha, evaluar enfoques secuenciales (bandits) en lugar de pruebas A/B fijas.
