# Experimentación y medición de impacto

Un buen AUC no prueba que el modelo genere valor. El impacto se mide comparando contra lo que habría pasado sin el modelo, y eso requiere un grupo de control diseñado antes de lanzar.

## Diseño del grupo de control

- **Aleatorio dentro de cada rating** (o banda de score), no global: así se puede medir el efecto por segmento y el control representa a todos los niveles de riesgo.
- **Tamaño por rating** según el riesgo y el costo de no actuar. Ejemplo usado en cobranzas: 3% del control en los ratings de menor riesgo, 5% en los intermedios y 8% en los de mayor riesgo.
- **Tamaño mínimo** para poder medir: `control mínimo = eventos objetivo / tasa esperada del evento`, por rating. Si no alcanza, alargar el período o agrupar ratings.
- **Exclusiones del control** por riesgo o por regulación (por ejemplo, deudas muy grandes que no se pueden dejar sin gestionar), documentadas y con su volumen.
- **Asignación determinista y reproducible** (hash del identificador con una semilla registrada).

## Control persistente entre corridas

Si el modelo se corre todos los días o todos los meses, reasignar el control desde cero en cada corrida lo contamina: una persona que fue control y después tratada ya no sirve para ninguna de las dos mediciones.

Asignación persistente ("sticky"), por rating:

1. Quien fue control sigue siendo control (aunque cambie de rating, manda el rating nuevo para el conteo).
2. Si falta para llegar al tamaño objetivo, se completa primero con personas **nuevas**, que no estaban en la corrida anterior.
3. Solo si todavía falta, se completa con ex-tratados.
4. Se registra la variante, la corrida y la versión del modelo en cada asignación.

## Medición

- **Intención de tratamiento (ITT):** se compara a todos los asignados a tratamiento contra todos los asignados a control, aunque algunos tratados no hayan recibido la acción. Es la estimación honesta del efecto de usar el modelo.
- Separar dos preguntas que suelen mezclarse:
  - **¿El modelo ordena?** AUC/KS y tasa por rating calculados **sobre el grupo de control**, donde el resultado no está afectado por la acción.
  - **¿La acción guiada por el modelo funciona?** Diferencia de resultados entre tratamiento y control (uplift), por rating.
- Reportar el impacto también en términos de negocio: pérdidas evitadas, recupero, costo de gestión, aprobaciones adicionales.

## Pilotos y bandas de prueba

- Antes del despliegue completo, un **backtest** sobre el día o el mes anterior con el dataset congelado, y un **piloto** con muestreo estratificado y monitoreo diario de los primeros días.
- Para validar un cambio de política o de corte (por ejemplo, aprobar por debajo del corte vigente), una **banda de prueba** controlada es la única forma de observar el desempeño real de la zona que hoy se rechaza (ver `06-sesgo-seleccion.md`).
- Experimentar también sobre la política, no solo sobre el modelo: probar dos o tres estrategias contra un control (por ejemplo, distintos aumentos de límite).
