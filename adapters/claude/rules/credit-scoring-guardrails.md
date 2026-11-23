# Guardrails de scoring crediticio

Reglas que aplican siempre en este proyecto. La metodología completa está en la skill `credit-scoring-ml`.

- La validación final es out-of-time. No reportar métricas de un split aleatorio como desempeño del modelo.
- No usar variables posteriores al punto de decisión: desempeño del propio préstamo (mora, atraso, castigo, refinanciación), ni variables de proceso (fecha o monto de desembolso, oferta final, analista).
- Binning, WoE, imputación, escalado y selección de variables se ajustan solo con train.
- La misma persona nunca aparece en dos particiones.
- No incluir cohortes cuya ventana de desempeño todavía no cerró.
- No usar variables sensibles (género, nacionalidad, estado civil, origen, religión, discapacidad) como features.
- AUC > 0.90 o IV > 0.5 en una variable: detenerse y revisar leakage antes de seguir.
- Antes de reportar métricas de un modelo nuevo, correr el chequeo de leakage sobre la lista final de features.
- Si alguna de estas reglas choca con lo pedido, decirlo en lugar de seguir en silencio.
