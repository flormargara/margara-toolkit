# Guardrails de scoring crediticio

Reglas específicas de crédito. Se usan junto con `ml-guardrails.md`, que tiene las reglas generales de ML. La metodología completa está en la skill `credit-scoring-ml`.

- La validación final es out-of-time y ninguna cohorte entra sin haber cumplido la ventana de desempeño.
- No usar variables posteriores a la solicitud: desempeño del propio préstamo (mora, atraso, castigo, refinanciación), variables de proceso (fecha o monto de desembolso, oferta final, analista) ni datos de buró consultados después de la evaluación.
- Binning y WoE se ajustan solo con train.
- No usar variables sensibles (género, nacionalidad, estado civil, origen, religión, discapacidad) como features.
- AUC > 0.90 o IV > 0.5 en una variable: detenerse y revisar leakage antes de seguir.
- Siempre hay un baseline de regresión logística sobre WoE y otro con la política de riesgo vigente.
- Si la PD se usa como número y el modelo se rebalanceó, recalibrarla.
- Los ratings se validan en una segunda muestra; un modelo nuevo no puede empeorar la calibración por rating.
- Si la acción guiada por el modelo cambia el resultado (cobranzas, límites), entrenar y evaluar solo con el grupo de control.
- El punto de corte lo decide el dueño del riesgo.
