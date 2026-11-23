# Guardrails de scoring crediticio

Reglas que aplican siempre en este proyecto. La metodología completa está en la skill `credit-scoring-ml`.

- La validación final es out-of-time. No reportar métricas de un split aleatorio como desempeño del modelo.
- No usar variables posteriores al punto de decisión: desempeño del propio préstamo (mora, atraso, castigo, refinanciación), ni variables de proceso (fecha o monto de desembolso, oferta final, analista).
- Binning, WoE, imputación, escalado y selección de variables se ajustan solo con train.
- La misma persona nunca aparece en dos particiones.
- No incluir cohortes cuya ventana de desempeño todavía no cerró.
- El filtro de elegibilidad es idéntico en train, validación y scoring.
- El early stopping y la búsqueda de hiperparámetros no usan el conjunto con el que se reporta el resultado.
- No usar variables sensibles (género, nacionalidad, estado civil, origen, religión, discapacidad) como features.
- AUC > 0.90, IV > 0.5 en una variable o una variable que concentra gran parte de la importancia: detenerse y revisar leakage antes de seguir.
- Antes de reportar métricas de un modelo nuevo, correr los chequeos de universo, leakage y concentración.
- Si la acción guiada por el modelo cambia el resultado (cobranzas, límites), entrenar y evaluar solo con el grupo de control.
- Un modelo nuevo reemplaza al vigente solo si lo supera por un margen mínimo y no empeora la calibración por rating.
- Si el código y la documentación se contradicen, seguir el código y avisar.
- Si alguna de estas reglas choca con lo pedido, decirlo en lugar de seguir en silencio.
