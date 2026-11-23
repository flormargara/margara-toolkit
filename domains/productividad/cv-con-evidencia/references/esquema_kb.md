# Fuentes del espacio personal

Las rutas siguientes se resuelven contra el espacio personal, no contra el skill.

| Archivo | Contenido y autoridad |
|---|---|
| `kb/kb_decisiones_canonicas.md` | Identidad, contacto, educación, cargos reales, instituciones y fechas. Fuente prioritaria para esos campos. |
| `kb/kb_experiencias.md` | Trabajo, investigación, proyectos, docencia y voluntariado confirmados. Organizar por experiencia con IDs estables, sin categorías obligatorias por profesión. |
| `kb/kb_capacidades.md` | Capacidad o método, experiencia que lo respalda, alcance, contexto, vigencia y límites. Referenciar la experiencia sin repetir su relato. |
| `kb/kb_preferencias_cv.md` | Confidencialidad, contacto a publicar, presentación, voz y adaptaciones durables confirmadas. |
| `ingreso/` | Fuentes recibidas, extracción provisional, confirmaciones y pendientes. Solo las confirmaciones y fuentes autorizadas respaldan las altas. |
| `aplicaciones/` | JD, estrategia, borradores, entregables, revisiones y registro. |
| `archivo/historial_perfil.md` | Altas y cambios con fecha, sección, valor anterior/nuevo y autorización. No es entrada habitual de una candidatura. |

## Forma de un bloque confirmado

En canónicas usá IDs para educación y cargos. Incluí nombres exactos, fechas con la precisión conocida, estado y respaldo. Una fecha desconocida sigue desconocida.

En experiencias usá un bloque por cuerpo de trabajo con:

```markdown
## E01. Nombre descriptivo del trabajo
- vínculo canónico: C01
- problema y propósito:
- contribución propia y colaboración:
- decisiones y dificultad:
- resultado y uso real:
- restricciones, límites y confidencialidad:
- capacidades y herramientas en contexto:
- respaldo: ingreso/confirmaciones.md, respuesta R01, IDs confirmados; o fuente primaria autorizada y pasaje
```

El esquema orienta la captura, no exige inventar campos. Omití los desconocidos y mantené la pregunta fuera de la KB. Una ausencia confirmada sí puede registrarse con alcance y fecha.

En capacidades diferenciá práctica actual, experiencia pasada, formación específica y conocimiento por lectura. Registrá último uso conocido y contexto. Un nombre amplio conserva el alcance de su experiencia: usar un servicio de nube no demuestra administrar toda la plataforma.

En preferencias guardá elecciones expresadas por la persona. Los valores predeterminados de formato viven en el método y no se convierten en preferencias confirmadas por copiar las plantillas.

## Registro de aplicaciones

Una ficha por candidatura terminada con ID único, empresa, puesto, destino, idioma, estado de envío, rutas de archivos, títulos mostrados, argumento, brechas, omisiones, preguntas resueltas y controles. Separá estado de preparación de estado de envío. Incluí SHA-256 de `cv.md` y estados de auditoría, revisión independiente y render.

Una corrección actualiza la ficha vigente y conserva las versiones reemplazadas en `versiones/` dentro de la aplicación. El registro ayuda a detectar contradicciones; los hechos siguen siendo propiedad de la KB.
