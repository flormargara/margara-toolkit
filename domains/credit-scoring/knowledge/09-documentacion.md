# Documentación

Un score no está terminado hasta que otra persona puede entender, reproducir y cuestionar cada decisión.

## Entregables mínimos

1. **Ficha del modelo** (`templates/model-card.md`): propósito, población, target, datos, variables, desempeño, limitaciones, uso permitido.
2. **Checklist de validación** (`templates/checklist-validacion.md`) completo, con cada punto marcado o con su excepción justificada.
3. **Diccionario de variables** finales: definición, fuente, fecha de disponibilidad, tratamiento de faltantes, dirección esperada del riesgo.
4. **Código reproducible**: un comando regenera la muestra, las particiones, el modelo y las métricas reportadas.
5. **Registro de decisiones**: qué alternativas se descartaron y por qué (definición de default, variables excluidas, tipo de modelo).

## Reproducibilidad

- Cada corrida productiva registra el tag **inmutable** de la imagen o del paquete (por ejemplo `sha-<commit>`), nunca `latest`.
- Cada predicción guardada lleva versión del modelo, fecha de scoreo y versión de la política o campaña que la usó (ver `12-trazabilidad.md`).
- Todas las entradas de un pipeline se leen con fecha explícita, de modo que sea imposible correrlo con una fecha equivocada sin que se note.

## La documentación tiene que coincidir con el código

La documentación desactualizada es peor que la ausente: quien la lee, persona o agente, saca conclusiones equivocadas con confianza.

- Generar la descripción de particiones, features y parámetros a partir de la configuración y el código, o validarla en CI.
- No copiar documentación de un repositorio a otro como plantilla sin reescribirla.
- Cuando el código y la documentación se contradicen, manda el código y se corrige la documentación en el mismo cambio.
- Para librerías y repositorios que van a tocar agentes, mantener un `AGENTS.md` con invariantes, trampas conocidas y qué no tocar sin coordinar (ver `shared/knowledge/agent-workflow.md`).

## Buenas prácticas de escritura

- Escribir para tres lectores: riesgo (metodología), negocio (impacto y corte), auditoría/regulador (trazabilidad).
- Cada número en la documentación indica de qué partición sale (train, test, OOT).
- Las limitaciones se escriben de forma explícita, no se esconden: población no cubierta, sesgo de selección, variables con riesgo de dejar de existir.
- Incluir fecha, versión del modelo y versión de los datos.
