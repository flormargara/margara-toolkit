# Guardrails de ML

Reglas que aplican siempre en este proyecto. La metodología completa está en la skill `ml-practices`.

- Con datos en el tiempo, la validación final es fuera de tiempo. No reportar métricas de un split aleatorio como desempeño del modelo.
- No usar variables posteriores al momento de la predicción.
- El filtro de elegibilidad es idéntico en train, validación y predicción.
- Imputación, escalado, encoding, selección de variables y sampling se ajustan solo con train.
- La misma entidad nunca aparece en dos particiones de la búsqueda (train, test, folds). La validación final se reporta completa y sin entidades vistas.
- No incluir filas cuyo horizonte del target todavía no se cumplió. Si la acción llega después de la predicción, el target se mide desde que se puede actuar.
- El early stopping y la búsqueda de hiperparámetros no usan el conjunto con el que se reporta el resultado. Un test usado para elegir se rotula como conjunto de selección.
- La selección de variables que mira el target vive dentro de train.
- Train, validación y scoring salen de la misma receta con distinto universo; `check_dataset.py` en verde antes de modelar.
- Siempre hay baselines y cada experimento cambia una sola cosa, con su fila en el leaderboard.
- Cada métrica va con su dispersión o intervalo; una diferencia menor que la dispersión es un empate.
- Un desempeño sospechosamente alto o una variable que concentra gran parte de la importancia: detenerse y revisar leakage antes de seguir.
- Antes de reportar métricas de un modelo nuevo, correr los chequeos de universo, leakage, dataset y concentración.
- Si la acción guiada por el modelo cambia el resultado, entrenar y evaluar solo con el grupo de control.
- Un modelo nuevo reemplaza al vigente solo si lo supera por un margen mínimo y no empeora la calibración.
- Si el código y la documentación se contradicen, seguir el código y avisar.
- Si alguna de estas reglas choca con lo pedido, decirlo en lugar de seguir en silencio.
