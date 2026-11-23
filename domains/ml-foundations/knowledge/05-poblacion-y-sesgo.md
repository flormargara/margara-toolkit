# Población de entrenamiento, población de predicción y sesgo de selección

Un modelo aprende de la población que tiene target y se aplica a la población que hay que decidir. Si no son la misma, el desempeño medido no vale para el uso real.

## Situaciones típicas

- **Sesgo de selección por la decisión vigente:** solo se observa el resultado de quienes pasaron por el proceso actual (aprobados, contactados, a quienes se mostró algo). El modelo nunca ve la parte que el proceso descartó.
- **Población nueva:** se entrena con clientes o casos con historia y se predice sobre nuevos, inactivos o un canal distinto.
- **Cambio de alcance:** el modelo se quiere usar para expandir a una zona que antes no se atendía.

## Qué hacer, como mínimo

1. **Cuantificar** qué parte de la población de predicción está representada en la de entrenamiento.
2. **Comparar** la distribución de las variables principales en ambas poblaciones y mostrar dónde el modelo va a extrapolar.
3. **Documentar** para qué población vale el desempeño medido.

## Validación adversarial

1. Unir ambas poblaciones y etiquetarlas (1 = población de entrenamiento, 0 = población de predicción).
2. Entrenar un clasificador que intente distinguirlas, usando las variables del modelo.
3. Si el AUC de ese clasificador está cerca de 0.5, las poblaciones son parecidas. Si es alto, son distintas y las variables que más lo explican muestran en qué.
4. Para corregir, entrenar el modelo con la parte de la población de entrenamiento **más parecida** a la de predicción (por ejemplo, el 20-40% con mayor probabilidad de pertenecer a la población de predicción, por período), o ponderar las filas por esa probabilidad.
5. Evaluar el clasificador adversarial con datos que no usó, y tratarlo como un modelo más: con versión, comparación contra la versión anterior y monitoreo.

## Registrar la predicción para todos

Si el modelo se ejecuta después de reglas que filtran, solo ve a quienes las pasaron y nunca se puede medir si es mejor que ellas. Calcular y **registrar la predicción para toda la población**, incluida la que las reglas excluyen, aunque la decisión siga a cargo de las reglas. Es la única forma de comparar modelo contra reglas, diseñar experimentos y tener datos para el próximo modelo.

## Cuando la acción cambia el resultado

Si el modelo decide a quién se trata (contactar, ofrecer, intervenir), el resultado de los tratados refleja el tratamiento y no el comportamiento original. Entrenar y evaluar con un **grupo de control** que no recibe la acción guiada por el modelo (ver `07-experimentacion.md`). Si no, el modelo aprende de su propio efecto.

## Observar la zona excluida

Para saber qué pasa en la parte de la población que el proceso vigente descarta, la única evidencia directa es una **prueba controlada**: actuar sobre una muestra acotada de esa zona y medir. Todas las técnicas de inferencia sin esa evidencia agregan supuestos que hay que documentar.
