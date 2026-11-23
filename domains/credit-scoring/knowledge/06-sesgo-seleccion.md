# Sesgo de selección, población objetivo y reject inference

Solo se observa el desempeño de quienes fueron aprobados. Un modelo de originación entrenado únicamente con aprobados aprende sobre una población que la política vigente ya filtró, y se aplica sobre todos los solicitantes.

## Por qué importa

- Las variables que la política vigente usa para rechazar aparecen con menos poder del que tienen, porque los casos extremos no están en la muestra.
- El modelo puede funcionar bien dentro de la zona aprobada y mal en la zona que antes se rechazaba, justo donde se lo va a usar para expandir.

## Qué hacer, como mínimo

1. **Cuantificar:** tasa de aprobación histórica y cómo cambió en el período de desarrollo. Con aprobación alta (por ejemplo mayor al 80%), el sesgo es menor.
2. **Comparar poblaciones:** distribución de las variables principales en solicitantes vs. aprobados. Mostrar dónde el modelo va a extrapolar.
3. **Documentar** que el desempeño medido vale para la población aprobada.

## Scorear a todos, también a los rechazados por reglas

Si el modelo se ejecuta después de las reglas de política, solo ve a quienes las pasaron y nunca se puede medir si ordena mejor que ellas. Calcular y **registrar el score de todos los solicitantes**, incluidos los que las reglas rechazan, aunque la decisión siga a cargo de las reglas. Es la única forma de comparar modelo contra reglas, diseñar experimentos de política y tener datos para el próximo modelo.

## Scoreabilidad y exclusiones por política

- Definir el **criterio mínimo de scoreabilidad**: con qué información mínima tiene sentido asignar un score. Los casos sin información suficiente (thin files) se tratan con otra política o con otro modelo, no con un score sin sentido.
- Excluir del desarrollo a quienes la política acepta o rechaza siempre de forma automática (empleados, casos especiales): el score no influye en su decisión y distorsionan la muestra.

## Cuando la población de entrenamiento no es la de predicción

Caso típico: se entrena con la cartera (tiene target) y se predice sobre no clientes, inactivos o reactivaciones (no tienen target). Medir la diferencia antes de confiar en el modelo.

**Validación adversarial:**

1. Unir ambas poblaciones y etiquetarlas (1 = población de entrenamiento, 0 = población de predicción).
2. Entrenar un clasificador que intente distinguirlas, usando las variables del score.
3. Si el AUC de ese clasificador está cerca de 0.5, las poblaciones son parecidas. Si es alto, son distintas y las variables que más lo explican muestran en qué.
4. Para corregir, entrenar el score con la parte de la población de entrenamiento **más parecida** a la de predicción (por ejemplo, el 20-40% con mayor probabilidad de pertenecer a la población de predicción, por período), o ponderar las filas por esa probabilidad.
5. Evaluar el clasificador adversarial con datos que no usó, y tratarlo como un modelo más: con versión, champion/challenger y monitoreo.

## Técnicas de reject inference

Ninguna recupera información que no existe; todas agregan supuestos. Usar con criterio y documentar el supuesto.

| Técnica | Idea | Riesgo |
|---|---|---|
| Parceling / fuzzy augmentation | Asignar a los rechazados un desempeño inferido según su score | Refuerza al modelo inicial; circular |
| Datos de buró de rechazados | Ver cómo pagaron los rechazados en otras entidades | La mejor opción si existe; requiere datos externos |
| Bandas de prueba (*below-cut testing*) | Aprobar una muestra controlada por debajo del corte | Es la única forma de observar el desempeño real; tiene costo de pérdidas |
| No inferir | Entrenar con aprobados y limitar el uso del modelo a esa zona | Honesto; no permite expandir aprobación con confianza |

## Recomendación

Si el objetivo es expandir la aprobación, proponer al negocio una banda de prueba controlada (ver `11-experimentacion.md`). Si no es posible, entrenar con aprobados, documentar la limitación y monitorear de cerca las nuevas aprobaciones en la zona antes rechazada.
