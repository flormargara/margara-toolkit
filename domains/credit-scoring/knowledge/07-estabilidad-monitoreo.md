# Estabilidad, monitoreo y reentrenamiento

## PSI (Population Stability Index)

Compara la distribución del score (o de una variable) entre una población de referencia y una actual.

PSI = Σ (actual% − referencia%) · ln(actual% / referencia%)

| PSI | Lectura | Acción |
|---|---|---|
| < 0.10 | Estable | Ninguna |
| 0.10 – 0.25 | Cambio moderado | Investigar causas (canal, campaña, política) |
| > 0.25 | Cambio significativo | Revisar desempeño; evaluar recalibración o reentrenamiento |

- Usar los mismos cortes (deciles de la referencia) para ambas poblaciones.
- Bins vacíos rompen el logaritmo: aplicar un piso pequeño (por ejemplo 0.0001).
- El **CSI** es el mismo cálculo por variable; sirve para encontrar qué variable explica un PSI alto.
- `checks/psi.py` implementa ambos. Para continuas también sirven KS de dos muestras o Wasserstein; para categóricas, chi² o Jensen-Shannon.

## En la validación

- PSI del score entre desarrollo y OOT.
- CSI de cada variable del modelo entre cohortes del período de desarrollo: descartar variables inestables antes de que lleguen al modelo final.

## En producción: tres capas

Cubrir primero la capa de negocio y después las demás.

| Capa | Qué | Cuándo se puede medir |
|---|---|---|
| **Negocio** | Tasa de malos esperada vs. observada por rating; distribución por rating; volumen de predicciones y % scoreado; tasa de aprobación; cambio de versión del modelo | Distribución y volumen, inmediato; tasas, al madurar la cohorte |
| **Modelo** | AUC/KS sobre cohortes maduras; PSI del score; CSI de variables; drift de importancias | PSI y CSI, inmediato; AUC/KS, al cerrar la ventana |
| **Datos** | Calidad de las fuentes; frescura de la última partición de cada tabla; tasa de faltantes por variable; categorías nuevas | Inmediato |

Detalles:

- **Cohortes por fecha de originación**, mensuales, a lo largo de toda la vida del modelo. Por cada cohorte madura: tasa de malos por decil o por rating. La pregunta es "¿sigue ordenando o está mezclando?".
- **Indicadores tempranos** (first payment default, 30+ a 3 meses) para alertar antes de que madure la ventana completa.
- **Si la acción cambia el resultado** (cobranzas, límites, ofertas), las métricas de desempeño del modelo se calculan sobre el **grupo de control**. Sobre los tratados, el modelo "se ve peor" justamente porque la gestión funcionó.
- **Drift de importancias**: comparar el ranking de importancias en producción con el de desarrollo (correlación de Spearman, coincidencia del top-N). Un cambio fuerte indica que el modelo está usando la información de otra forma.
- **Presupuesto de drift**: alertar cuando derivan más de N variables (o una proporción) en lugar de alertar por cada una, con umbrales más estrictos para las variables más importantes.
- En modelos en tiempo real, las métricas de uso son las únicas inmediatas. Dejar escrito qué se mide y cuándo.

Definir de antemano umbrales de alerta, canal de aviso y quién actúa ante cada uno. Un monitoreo sin dueño ni umbrales no sirve. Las métricas se guardan en un almacén central con historia para ver tendencias, no solo el último valor.

## Recalibrar vs. reentrenar

- **Recalibrar** (ajustar el nivel de la PD o los cortes de rating) cuando el orden se mantiene pero cambió la tasa de malos promedio.
- **Reentrenar** cuando cae la discriminación, cambia la población de forma estructural o aparecen nuevas fuentes de datos.

## Promoción: champion, challenger o recalibrado

Cada reentrenamiento compara tres candidatos sobre la misma cohorte madura que ninguno usó para entrenar:

1. **Champion**: el modelo vigente.
2. **Recalibrado**: el modelo vigente con cortes o nivel ajustados.
3. **Challenger**: el modelo reentrenado.

Reglas:

- El challenger gana solo si mejora AUC **y** KS por un **margen mínimo** acordado (o si el intervalo de confianza por bootstrap de la diferencia no incluye cero) **y** no empeora el error de calibración por rating.
- Si no, el recalibrado gana si reduce el error de calibración por rating respecto del champion.
- En cualquier otro caso, o si faltan datos, se queda el champion.

Una mejora de 0.001 en AUC es ruido: reemplazar un modelo tiene costos (recalibrar, comunicar, monitorear).

## Reentrenamiento automático

- Ningún reentrenamiento automático publica un modelo sin pasar por la regla de promoción.
- **Bucle de retroalimentación:** si el modelo decide a quién se trata (cobranzas, límites), los resultados de los tratados reflejan el tratamiento y no el riesgo original. Entrenar con el grupo de control, o incluir el tratamiento recibido como variable y neutralizarlo al predecir. Si no, el modelo aprende de su propio efecto y con el tiempo subestima el riesgo de los segmentos mejor gestionados.

## Comunicación de resultados

Toda afirmación de mejora del modelo va con evidencia de desempeño: tasa observada por rating y AUC/KS en una cohorte madura. Un cambio en la distribución de ratings después de cambiar de modelo, por sí solo, no prueba que el nuevo modelo detecte mejor: también puede ser drift o mala calibración.
