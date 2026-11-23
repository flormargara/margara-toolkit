# Sesgo de selección y reject inference en crédito

Aplica todo `ml-foundations/knowledge/05-poblacion-y-sesgo.md`: comparación de poblaciones, validación adversarial, registrar la predicción para todos y entrenar con control cuando la acción cambia el resultado. Acá está lo propio de crédito.

## Aprobados vs. solicitantes

Solo se observa el desempeño de quienes fueron aprobados y tomaron el crédito. Un modelo de originación entrenado únicamente con ellos aprende sobre una población que la política vigente ya filtró, y se aplica sobre todos los solicitantes.

- Las variables que la política usa para rechazar aparecen con menos poder del que tienen, porque los casos extremos no están en la muestra.
- El modelo puede funcionar bien dentro de la zona aprobada y mal en la zona que antes se rechazaba, justo donde se lo va a usar para expandir.
- Cuantificar la tasa de aprobación histórica y cómo cambió en el período. Con aprobación alta (por ejemplo mayor al 80%), el sesgo es menor.

## Scorear también a los rechazados por reglas

Si el score se calcula después de las reglas de política, nunca se puede medir si es mejor que ellas. Calcular y registrar el score de **todos los solicitantes**, incluidos los rechazados por reglas, aunque la decisión siga a cargo de las reglas.

## Scoreabilidad y exclusiones por política

- Definir el **criterio mínimo de scoreabilidad**: con qué información mínima tiene sentido asignar un score. Los casos sin información suficiente (thin files) se tratan con otra política o con un score new to credit.
- Excluir del desarrollo a quienes la política acepta o rechaza siempre de forma automática (empleados, casos especiales, extranjeros si aplica, fallecidos): el score no influye en su decisión y distorsionan la muestra.

## Población de entrenamiento distinta de la de predicción

Casos típicos en crédito: new to credit (se entrena con la cartera y se predice sobre no clientes), reactivación y cross-sell (se entrena con clientes activos y se predice sobre inactivos en un producto). Usar la validación adversarial de `ml-foundations/knowledge/05-poblacion-y-sesgo.md` para medir la diferencia y entrenar con la parte de la cartera más parecida a la población de predicción.

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
