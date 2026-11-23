# Auditar contenido y entrega

Auditá como trabajo ajeno. Abrí JD, estrategia, CV, canónicas, preferencias, experiencias y capacidades activas; consultá las fichas vigentes para consistencia. Un dato factual nuevo sigue `actualizar_perfil.md`. Una selección nueva actualiza estrategia antes de redactar.

## Antes de exportar

1. Comprobá cada afirmación contra estrategia y KB, con fuente y sección: autoría, alcance, adopción, causalidad, métricas, fechas, nivel, confidencialidad y educación. Una equivalencia educativa requiere respaldo propio, no una preferencia importada de otro candidato.
2. Compará la conclusión de una lectura de veinte segundos con la estrategia. Cada mensaje debe probar una contribución, agregar algo distinto y poder defenderse en entrevista. Aplicá el control por bullet de `criterio_editorial_cv.md`.
3. Revisá amplitud y tareas decisivas. La prueba más fuerte debe estar visible; el número de herramientas no sustituye profundidad. Comprobá el mapa de capacidades, métodos y tecnologías con sus límites, incluidas las respaldadas por experiencias que no tienen bullet.
4. Probá una lectura de diez segundos de nombre, posicionamiento, títulos, orden e inicios de bullets. Debe contar el mismo argumento. Revisá cada experiencia como conjunto para evitar fragmentación y repeticiones.
5. Registrá en `auditoria.md` ajuste y brechas, omisión más costosa y afirmación más discutible, con justificación o corrección. Separá cumplimiento mecánico, calidad editorial y competitividad.
6. Ejecutá `revision_senior_cv.md` con el contexto y la independencia allí definidos. Conservá diagnóstico, resolución de objeciones y SHA-256 del contenido vigente. Una objeción material abierta mantiene pendiente la aprobación.
7. Aplicá `voz.md` y `formato_cv.md`. Generá TXT con `exportar_cv.py --solo-texto` si todavía no está. Ejecutá `lint_cv.py --cv <cv.txt> --kb <espacio>/kb` sin PDF. Un resultado 0 solo aprueba controles mecánicos parciales.

## Después de exportar

Seguí `entregables.md`. Ejecutá el lint con el PDF y la extensión registrada. Verificá texto seleccionable, paridad con la fuente, número de páginas y render de todas las páginas. Revisá alineaciones, fuentes, cortes y legibilidad. Una página breve obliga a revisar selección; una omisión justificada permite cerrar con espacio en blanco.

El lint detecta años y métricas ausentes como avisos: la aparición de un número en otra experiencia tampoco confirma una afirmación. Seniority se contrasta manualmente con el cargo real y las adaptaciones autorizadas. Tener un cargo senior confirmado es válido.

Si cambia `cv.md` después de su aprobación, reabrí la revisión de lo afectado y actualizá su hash. El archivo de auditoría registra controles realmente ejecutados, archivos vigentes, estados y limitaciones; nunca marca como comprobado un paso que faltó ejecutar.

## Registro y cierre

Actualizá la ficha según `esquema_kb.md`. La entrega completa requiere hechos respaldados, selección justificada, revisión independiente resuelta y formatos vigentes verificados. Si faltan capacidades del entorno, entregá lo completado con estados separados de contenido, revisión y archivos. La revisión pendiente conserva su nombre; el límite de rondas no equivale a aprobación.
