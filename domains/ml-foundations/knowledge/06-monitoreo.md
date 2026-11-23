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
- `checks/psi.py` implementa ambos. Para continuas también sirven KS de dos muestras, Wasserstein o Cramér-von Mises; para categóricas, chi² o Jensen-Shannon.

En la validación: PSI de la predicción entre desarrollo y validación final, y CSI de cada variable entre períodos de desarrollo para descartar las inestables antes del modelo final.

## En producción: tres capas

Cubrir primero la capa de negocio y después las demás.

| Capa | Qué | Cuándo se puede medir |
|---|---|---|
| **Negocio** | Resultado esperado vs. observado por grupo o banda de predicción; distribución por grupo; volumen de predicciones y % cubierto; cambio de versión del modelo | Distribución y volumen, inmediato; resultados, cuando se cumple el horizonte |
| **Modelo** | Métrica principal sobre cohortes maduras; PSI de la predicción; CSI de variables; drift de importancias | PSI y CSI, inmediato; métrica, al cerrar el horizonte |
| **Datos** | Calidad de las fuentes; frescura de la última partición de cada tabla; tasa de faltantes por variable; categorías nuevas | Inmediato |

Detalles:

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

- El challenger gana solo si mejora la métrica principal (y las secundarias acordadas) por un **margen mínimo** o si el intervalo de confianza por bootstrap de la diferencia no incluye cero, **y** no empeora la calibración.
- Si no, el recalibrado gana si reduce el error de calibración respecto del champion.
- En cualquier otro caso, o si faltan datos, se queda el champion.

Una mejora mínima es ruido: reemplazar un modelo tiene costos (recalibrar, comunicar, monitorear).

## Reentrenamiento automático

- Ningún reentrenamiento automático publica un modelo sin pasar por la regla de promoción.
- **Bucle de retroalimentación:** si el modelo decide a quién se trata, se entrena con el grupo de control (ver `05-poblacion-y-sesgo.md`).

## Comunicación de resultados

Toda afirmación de mejora del modelo va con evidencia de desempeño en cohortes maduras. Un cambio en la distribución de las predicciones después de cambiar de modelo, por sí solo, no prueba que el nuevo sea mejor: también puede ser drift o mala calibración.
