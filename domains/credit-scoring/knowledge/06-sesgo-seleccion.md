# Sesgo de selección y reject inference

Solo se observa el desempeño de quienes fueron aprobados. Un modelo de originación entrenado únicamente con aprobados aprende sobre una población que la política vigente ya filtró, y se aplica sobre todos los solicitantes.

## Por qué importa

- Las variables que la política vigente usa para rechazar aparecen con menos poder del que tienen, porque los casos extremos no están en la muestra.
- El modelo puede funcionar bien dentro de la zona aprobada y mal en la zona que antes se rechazaba, justo donde se lo va a usar para expandir.

## Qué hacer, como mínimo

1. **Cuantificar:** tasa de aprobación histórica y cómo cambió en el período de desarrollo. Con aprobación alta (por ejemplo mayor al 80%), el sesgo es menor.
2. **Comparar poblaciones:** distribución de las variables principales en solicitantes vs. aprobados. Mostrar dónde el modelo va a extrapolar.
3. **Documentar** que el desempeño medido vale para la población aprobada.

## Técnicas de reject inference

Ninguna recupera información que no existe; todas agregan supuestos. Usar con criterio y documentar el supuesto.

| Técnica | Idea | Riesgo |
|---|---|---|
| Parceling / fuzzy augmentation | Asignar a los rechazados un desempeño inferido según su score | Refuerza al modelo inicial; circular |
| Datos de buró de rechazados | Ver cómo pagaron los rechazados en otras entidades | La mejor opción si existe; requiere datos externos |
| Bandas de prueba (*below-cut testing*) | Aprobar una muestra controlada por debajo del corte | Es la única forma de observar el desempeño real; tiene costo de pérdidas |
| No inferir | Entrenar con aprobados y limitar el uso del modelo a esa zona | Honesto; no permite expandir aprobación con confianza |

## Recomendación

Si el objetivo es expandir la aprobación, proponer al negocio una banda de prueba controlada. Si no es posible, entrenar con aprobados, documentar la limitación y monitorear de cerca las nuevas aprobaciones en la zona antes rechazada.
