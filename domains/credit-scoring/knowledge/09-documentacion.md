# Documentación

Un score no está terminado hasta que otra persona puede entender, reproducir y cuestionar cada decisión.

## Entregables mínimos

1. **Ficha del modelo** (`templates/model-card.md`): propósito, población, target, datos, variables, desempeño, limitaciones, uso permitido.
2. **Checklist de validación** (`templates/checklist-validacion.md`) completo, con cada punto marcado o con su excepción justificada.
3. **Diccionario de variables** finales: definición, fuente, fecha de disponibilidad, tratamiento de faltantes, dirección esperada del riesgo.
4. **Código reproducible**: un comando regenera la muestra, las particiones, el modelo y las métricas reportadas.
5. **Registro de decisiones**: qué alternativas se descartaron y por qué (definición de default, variables excluidas, tipo de modelo).

## Buenas prácticas de escritura

- Escribir para tres lectores: riesgo (metodología), negocio (impacto y corte), auditoría/regulador (trazabilidad).
- Cada número en la documentación indica de qué partición sale (train, test, OOT).
- Las limitaciones se escriben de forma explícita, no se esconden: población no cubierta, sesgo de selección, variables con riesgo de dejar de existir.
- Incluir fecha, versión del modelo y versión de los datos.
