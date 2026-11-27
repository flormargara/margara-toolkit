# Documentación y reproducibilidad

Un modelo no está terminado hasta que otra persona puede entender, reproducir y cuestionar cada decisión.

## Entregables mínimos

1. **Ficha del modelo** (`templates/model-card.md`): propósito, población, target, datos, variables, desempeño, limitaciones, uso permitido.
2. **Checklist de validación** (`templates/checklist-validacion.md`) completo, con cada punto marcado o con su excepción justificada.
3. **Diccionario de variables** finales: definición, fuente, fecha de disponibilidad, tratamiento de faltantes, dirección esperada del efecto.
4. **Código reproducible:** un comando regenera la muestra, las particiones, el modelo y las métricas reportadas.
5. **Registro de decisiones y experimentos:** qué alternativas se descartaron y por qué.

## Reproducibilidad

- Cada corrida productiva registra el tag **inmutable** de la imagen o del paquete (por ejemplo `sha-<commit>`), nunca `latest`.
- Cada predicción guardada lleva versión del modelo y fecha de predicción.
- Todas las entradas de un pipeline se leen con fecha explícita, de modo que sea imposible correrlo con una fecha equivocada sin que se note.
- Semillas fijas en sampling, particiones y entrenamiento.

## Pasar a producción

Errores que aparecen al convertir el código de desarrollo en un pipeline que corre solo, sea cual sea la plataforma:

- **Guardar el set de entrenamiento junto al modelo:** features, target e ids de cada fila, no solo el modelo entrenado. Sin eso no se puede auditar qué aprendió ni reentrenar igual.
- **Separar lo que se despliega de lo que es trazabilidad.** El artefacto que usa la inferencia (modelo, encoders, umbrales) va en el paquete desplegable; los datos de entrenamiento y los reportes se guardan para auditoría, no viajan con el modelo.
- **Contrato entre pasos:** antes de implementar un paso, verificar que el nombre, la ubicación y el formato del archivo que escribe sean los que lee el paso siguiente.
- **Predicciones en escala de negocio.** Si el modelo se entrenó con el target transformado (por ejemplo en logaritmo), se revierte antes de guardar o pasar la predicción a otro paso; nunca se propaga el valor transformado (ver `04-modelado.md`).
- **La ventana temporal sale de la fecha de ejecución.** El fin del período del universo de scoring se toma de la fecha con la que corre el pipeline, no se deriva de otra fecha más un desfase que puede desalinearse.
- **Lo que no está implementado no se despliega.** Un paso o un flujo incompleto se comenta o se excluye del despliegue; dejarlo a medio hacer rompe el resto.
- **Confirmar qué está vivo antes de corregir.** Verificar qué archivo, configuración o tabla usa realmente el pipeline antes de cambiarlo: es común arreglar una versión que quedó en desuso. Lo mismo con los nombres de tablas: se confirman contra la fuente, no se suponen.
- **Sin configuración muerta.** Las constantes y parámetros que nadie lee se borran; confunden a quien mantiene y a los agentes.

## La documentación tiene que coincidir con el código

La documentación desactualizada es peor que la ausente: quien la lee, persona o agente, saca conclusiones equivocadas con confianza.

- Generar la descripción de particiones, features y parámetros a partir de la configuración y el código, o validarla en CI.
- No copiar documentación de un repositorio a otro como plantilla sin reescribirla.
- Cuando el código y la documentación se contradicen, manda el código y se corrige la documentación en el mismo cambio.
- Para librerías y repositorios que van a tocar agentes, mantener un `AGENTS.md` con invariantes, trampas conocidas y qué no tocar sin coordinar (ver `shared/knowledge/agent-workflow.md`).

## Buenas prácticas de escritura

- Escribir para tres lectores: quien mantiene el modelo (metodología), quien lo usa (impacto y umbral) y quien lo audita (trazabilidad).
- Cada número en la documentación indica de qué partición sale.
- Las limitaciones se escriben de forma explícita: población no cubierta, sesgo de selección, variables con riesgo de dejar de existir.
- Incluir fecha, versión del modelo y versión de los datos.
