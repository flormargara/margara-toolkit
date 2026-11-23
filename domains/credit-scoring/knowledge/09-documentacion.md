# Documentación de scores de crédito

Aplica todo `ml-foundations/knowledge/09-documentacion.md`: entregables mínimos, reproducibilidad con tags inmutables y documentación verificada contra el código. Acá está lo propio de crédito.

## Entregables

- **Ficha del modelo de crédito** (`templates/model-card.md`): agrega a la general la definición de default, la tabla de ratings, el anclaje de puntos, el análisis de punto de corte y la sección de equidad.
- **Checklist de crédito** (`templates/checklist-validacion.md`): agrega a la general los puntos de roll rate, WoE/IV, ratings, reject inference y equidad.
- Matriz de roll rate usada para definir el default.

## Lectores

- **Riesgo:** metodología, definición de default, calibración por rating.
- **Negocio:** impacto en aprobación y mora, opciones de punto de corte.
- **Auditoría y regulador:** trazabilidad, reason codes, variables sensibles, validación independiente, historial de cambios aprobados.

## Gobierno

- Inventario de modelos con dueño, versión, fecha de aprobación y próxima revisión.
- Validación independiente antes de producción cuando la organización lo requiera.
- Registro de cambios con justificación y aprobación.
