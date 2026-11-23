# Guardrails de ML

Reglas que aplican siempre en este proyecto. La metodología completa está en la skill `ml-practices`.

- Con datos en el tiempo, la validación final es fuera de tiempo. No reportar métricas de un split aleatorio como desempeño del modelo.
- No usar variables posteriores al momento de la predicción.
- El filtro de elegibilidad es idéntico en train, validación y predicción.
- Imputación, escalado, encoding, selección de variables y sampling se ajustan solo con train.
- La misma entidad nunca aparece en dos particiones.
- No incluir filas cuyo horizonte del target todavía no se cumplió.
- El early stopping y la búsqueda de hiperparámetros no usan el conjunto con el que se reporta el resultado.
- Siempre hay baselines y cada experimento cambia una sola cosa.
- Un desempeño sospechosamente alto o una variable que concentra gran parte de la importancia: detenerse y revisar leakage antes de seguir.
- Antes de reportar métricas de un modelo nuevo, correr los chequeos de universo, leakage y concentración.
- Si la acción guiada por el modelo cambia el resultado, entrenar y evaluar solo con el grupo de control.
- Un modelo nuevo reemplaza al vigente solo si lo supera por un margen mínimo y no empeora la calibración.
- Si el código y la documentación se contradicen, seguir el código y avisar.
- Si alguna de estas reglas choca con lo pedido, decirlo en lugar de seguir en silencio.
