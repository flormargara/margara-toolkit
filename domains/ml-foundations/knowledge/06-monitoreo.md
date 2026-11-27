# Estabilidad, monitoreo y reentrenamiento

## Drift de datos y de predicciones

**PSI (Population Stability Index):** compara la distribución de una variable o de la predicción entre una población de referencia y una actual.

PSI = Σ (actual% − referencia%) · ln(actual% / referencia%)

| PSI | Lectura | Acción |
|---|---|---|
| < 0.10 | Estable | Ninguna |
| 0.10 – 0.25 | Cambio moderado | Investigar causas |
| > 0.25 | Cambio significativo | Revisar desempeño; evaluar recalibración o reentrenamiento |

- Usar los mismos cortes (deciles de la referencia) para ambas poblaciones.
- Bins vacíos rompen el logaritmo: aplicar un piso pequeño (por ejemplo 0.0001).
- El **CSI** es el mismo cálculo por variable; sirve para encontrar qué variable explica un PSI alto.
- `checks/psi.py` implementa ambos. Para continuas también sirven Wasserstein o Cramér-von Mises; para categóricas, Jensen-Shannon.
- Preferir medidas de magnitud con umbrales fijos (PSI, Wasserstein) antes que p-valores (KS, chi²). El p-valor depende del tamaño de la muestra: con el período completo casi todo "deriva", y sobre una muestra chica el resultado cambia según qué filas tocaron. Si se usa una prueba con p-valor, fijar y documentar el tamaño de la muestra.

En la validación: PSI de la predicción entre desarrollo y validación final, y CSI de cada variable entre períodos de desarrollo para descartar las inestables antes del modelo final.

## En producción: tres capas

Cubrir primero la capa de negocio y después las demás.

| Capa | Qué | Cuándo se puede medir |
|---|---|---|
| **Negocio** | Resultado esperado vs. observado por grupo o banda de predicción; distribución por grupo; volumen de predicciones y % cubierto; cambio de versión del modelo | Distribución y volumen, inmediato; resultados, cuando se cumple el horizonte |
| **Modelo** | Métrica principal sobre cohortes maduras; PSI de la predicción; CSI de variables; drift de importancias | PSI y CSI, inmediato; métrica, al cerrar el horizonte |
| **Datos** | Calidad de las fuentes; frescura de la última partición de cada tabla; tasa de faltantes por variable; categorías nuevas | Inmediato |

### Contra qué se compara

- **Drift:** la referencia son los datos y las predicciones del **modelo vigente** en producción. No los del último reentrenamiento que perdió la promoción: eso mide drift contra una referencia que nunca estuvo en producción.
- **Desempeño:** la referencia es la métrica de la **validación final** documentada para la versión vigente, no la de test (que suele ser un conjunto de selección y está inflada, lo que genera falsas alarmas).
- Sin referencia documentada para la versión, el indicador queda en gris (sin evaluar), nunca en verde. Un modelo que aparece en producción sin configuración de monitoreo es una alerta.
- Si el modelo se recalibra sin cambiar de versión, comparar dentro de la misma grilla de bandas y registrar cada cambio de grilla como un evento.

### Cuándo un desvío es un hallazgo

- Solo sobre **cohortes maduras** (el horizonte ya se cumplió).
- Solo si el **intervalo de confianza del valor observado excluye el esperado**, no por la diferencia puntual.
- Lo que todavía no maduró, o no cumple lo anterior, se marca "a vigilar" y no dispara acciones.
- Umbrales simples para la métrica principal: alerta si empeora 10% o más respecto de la referencia, crítico si empeora 20% o más. Ajustarlos por modelo y dejarlos escritos.

### Gate de calidad de entradas

Antes de cada corrida de inferencia o entrenamiento, una señal pasa / no pasa por tabla de entrada:

- **Esquema:** nombres y tipos de columnas iguales a los esperados.
- **Volumen:** la partición no está vacía y no cae más de un umbral respecto de la anterior.
- **Disponibilidad y frescura:** la partición esperada existe y está actualizada a la fecha de corte.

Si no pasa, la corrida no publica predicciones (falla cerrada) y avisa. Una tabla rota puede producir que nadie reciba una oferta o que todos la reciban. Mantener un inventario de qué tablas consume cada modelo, con su esquema esperado y su criticidad, para saber qué vigilar primero.

`checks/check_inputs.py` aplica el gate: el inventario es su contrato (JSON, una entrada por tabla con columnas y tipos, filas mínimas, caída máxima, antigüedad máxima y criticidad) y el estado observado sale de dos queries baratas, el esquema de `information_schema.columns` y las filas por partición. Sale con error si una tabla crítica no pasa, así el pipeline no publica.

Detalles:

- **Demora del ground truth:** dejar escrito cuánto tarda en llegar y programar el monitoreo de desempeño en consecuencia. Mientras no hay ground truth se monitorea solo drift, y se dice.
- **Cohortes por fecha de predicción**, a lo largo de toda la vida del modelo. Por cada cohorte madura: métrica y resultado por decil o banda. La pregunta es "¿sigue ordenando o está mezclando?".
- **Indicadores tempranos** que anticipen el resultado antes de que se cumpla el horizonte completo.
- **Si la acción cambia el resultado**, las métricas de desempeño se calculan sobre el **grupo de control**. Sobre los tratados, el modelo "se ve peor" justamente porque la acción funcionó.
- **Drift de importancias:** comparar el ranking de importancias en producción con el de desarrollo (correlación de Spearman, coincidencia del top-N). Un cambio fuerte indica que el modelo usa la información de otra forma.
- **Presupuesto de drift:** alertar cuando derivan más de N variables (o una proporción) en lugar de alertar por cada una, con umbrales más estrictos para las variables más importantes.
- En modelos en tiempo real, las métricas de uso son las únicas inmediatas. Dejar escrito qué se mide y cuándo.
- En regresión: error (MAE, RMSE) contra el valor real cuando llega, histograma de predicciones y estabilidad de la predicción por entidad.

Definir de antemano umbrales de alerta, canal de aviso y quién actúa ante cada uno. Un monitoreo sin dueño ni umbrales no sirve. Las métricas se guardan en un almacén central con historia para ver tendencias, no solo el último valor.

## Recalibrar vs. reentrenar

- **Recalibrar** (ajustar el nivel de la predicción o los umbrales) cuando el orden se mantiene pero cambió el nivel del evento.
- **Reentrenar** cuando cae la discriminación, cambia la población de forma estructural o aparecen nuevas fuentes de datos.

## Promoción: champion, challenger o recalibrado

Cada reentrenamiento compara tres candidatos sobre la misma cohorte madura que ninguno usó para entrenar:

1. **Champion:** el modelo vigente.
2. **Recalibrado:** el modelo vigente con nivel o umbrales ajustados.
3. **Challenger:** el modelo reentrenado.

Reglas:

- El challenger gana solo si mejora la métrica principal (y las secundarias acordadas) por un **margen mínimo** o si el intervalo de confianza por bootstrap de la diferencia no incluye cero, **y** no empeora la calibración. "Mejora mayor que cero" no alcanza. Exigir que mejoren a la vez varias métricas o vistas sin margen tampoco: con ruido, pasa o falla por azar.
- Si no, el recalibrado gana si reduce el error de calibración respecto del champion.
- En cualquier otro caso, o si faltan datos, se queda el champion.

Una mejora mínima es ruido: reemplazar un modelo tiene costos (recalibrar, comunicar, monitorear).

`checks/promotion.py` aplica esta regla sobre la cohorte, con AUC como métrica de orden y el error de calibración por deciles; el margen, la tolerancia y el filtro del grupo de control se pasan por parámetro y se dejan escritos en la spec.

## Reentrenamiento automático

- Ningún reentrenamiento automático publica un modelo sin pasar por la regla de promoción.
- La política de reentrenamiento automático arranca en "solo notificar" y se activa recién cuando los umbrales se validaron con algunos ciclos reales.
- **Reentrenar o hacer una versión nueva.** Reentrenar es mantenimiento: mismo problema, mismo target, mismo uso, datos nuevos. Una versión nueva es rediseño: cambió el negocio o el proceso, se piden otros outputs, ventanas o segmentos, hace falta otro target u otras fuentes, o hay problemas estructurales de calibración o cobertura. Antes de una versión nueva, preguntar a quien usa el modelo qué decisiones se tomaron realmente con él, qué le resultó útil, qué lo frustró y qué evidencia necesita para confiar en la nueva.
- **Bucle de retroalimentación:** si el modelo decide a quién se trata, se entrena con el grupo de control (ver `05-poblacion-y-sesgo.md`).

## Comunicación de resultados

Toda afirmación de mejora del modelo va con evidencia de desempeño en cohortes maduras. Un cambio en la distribución de las predicciones después de cambiar de modelo, por sí solo, no prueba que el nuevo sea mejor: también puede ser drift o mala calibración.
