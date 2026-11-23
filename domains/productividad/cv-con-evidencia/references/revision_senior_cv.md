# Revisión senior independiente

Filtro editorial final de contenido, antes de generar DOCX/PDF. Se aplica a CVs nuevos y a auditorías de CVs existentes. Complementa el gate factual de `auditoria_cv.md`.

## Encargo y contexto limpio

Leé `entorno.md` para crear un revisor con contexto limpio en el agente disponible. Pasale este documento, `criterio_editorial_cv.md`, la ruta de `jd.md` y la de `cv.md`. La primera lectura recibe únicamente esos materiales sobre la candidatura. Estrategia, conversaciones, borradores y auditorías anteriores se comparten después del diagnóstico inicial. Si no hay delegación disponible, prepará el encargo para una sesión independiente y dejá la revisión pendiente. La autolectura no cumple independencia.

Asumí el rol de un par senior del área que participa en la contratación. Tenés poco tiempo y querés saber qué trabajo podría confiarse a esta persona y qué evidencia permite hacerlo. Tu criterio es senior; el candidato se evalúa contra el puesto real, sin exigirle trayectoria, impacto o autoridad que la JD no pide.

Cuestioná el texto con razones concretas. No juzgues la personalidad del candidato ni produzcas una caricatura hostil. Podés conservar todos los bullets si cada uno aporta evidencia distinta. No hay una cuota de objeciones ni de recortes.

## Primera lectura. Valor para quien contrata

Leé la JD y luego el CV completo. Escribí la conclusión profesional que deja, antes de analizar sus bullets. Identificá qué tareas de la contratación tienen prueba y cuáles quedan abiertas.

Revisá todos los bullets de experiencia e investigación, incluidos los que conservarías. Usá IDs estables por experiencia y posición, por ejemplo `E01-1`, `E02-2`. Para cada uno:

1. Expresá qué contribución demuestra y qué decisión de contratación ayuda a tomar. Puede aportar ajuste directo, profundidad o una capacidad complementaria.
2. Aplicá `De evidencia a contribución` de `criterio_editorial_cv.md`. Indicá qué diferencia concreta hace cada detalle relevante en la evaluación de ese trabajo. Leé esa referencia durante la primera lectura; aporta criterio editorial, no evidencia sobre el candidato.
3. Preguntá qué distingue el aporte de una implementación rutinaria para ese puesto. Una lista de componentes, una práctica básica o un incidente aislado necesita contexto para justificar su protagonismo. Si el trabajo es relevante pero está mal presentado, conservá el trabajo y cuestioná su redacción.
4. Contrastá con los demás bullets. Señalá repeticiones, enumeraciones fragmentadas y evidencia de mayor valor desplazada. Recomendá eliminar solo cuando no quede una contribución distinta que recuperar.

Revisá también resumen, Skills y negritas con el mismo criterio. Comprobá que Skills permite reconocer trabajos y métodos que el candidato sabe ejercer y que la primera lectura da importancia a la contribución elegida.

La precisión técnica tiene valor cuando cambia la evaluación del trabajo. No reemplaces un mecanismo informativo por frases como "solución robusta", "sistema escalable" o "impacto estratégico". Un término técnico exacto no necesita una explicación para principiantes.

Entregá el diagnóstico inicial antes de recibir evidencia. Por bullet, indicá: ID, contribución percibida, detalle que gana o pierde su lugar con el motivo, y decisión `conservar`, `reescribir`, `fusionar` o `eliminar`. Citá el fragmento cuestionado. Una preferencia de estilo sin pérdida identificable de claridad, credibilidad o relevancia es opcional, no bloqueante.

## Segunda lectura. Corregir sin inflar

Después del diagnóstico inicial, el coordinador envía `estrategia.md` y los pasajes de la KB activa que respaldan los bullets cuestionados, con sus rutas y secciones. El revisor puede pedir el contexto necesario de esas fuentes. La estrategia fija hechos y límites, pero su justificación editorial puede cuestionarse.

Para cada cambio propuesto, devolvé el texto original, una propuesta en el idioma del CV y el hecho autorizado que la sostiene. Si falta evidencia para una formulación más fuerte, indicá el límite y proponé una versión conservadora. No conviertas intención en uso, persistencia en fiabilidad probada, múltiples casos en diversidad validada ni trabajo propio en adopción por terceros.

Si la propuesta requiere evidencia ya confirmada que falta en la estrategia, el coordinador actualiza la estrategia antes de redactar. Si requiere un hecho nuevo, sigue la ruta factual de las maestras. El revisor no edita la KB ni los entregables.

## Iteración y cierre

El coordinador integra los cambios respaldados y registra los rechazos con una razón concreta. Un cambio de selección vuelve a la estrategia. Toda redacción nueva pasa por el gate factual de `auditoria_cv.md`.

El mismo revisor recibe el CV completo revisado y verifica sus objeciones, los bullets modificados y el argumento conjunto. Si una corrección cambia selección, orden o significado de otros bullets, revisa también los afectados. Resuelve o mantiene cada objeción explícitamente, sin inventar nuevos criterios para justificar otra ronda.

Permití hasta tres rondas de diagnóstico y corrección. Si persiste una objeción material, registrá el desacuerdo y dejá el filtro pendiente; el límite de rondas no equivale a aprobación. Un desacuerdo de estilo puede cerrarse con el motivo registrado, sin pedir confirmación rutinaria a la persona candidata.

Guardá en `revision_senior.md` dentro de la aplicación: conclusión inicial, diagnóstico de cada bullet, propuestas y respaldo, decisiones del coordinador y estado final de las objeciones. Identificá la versión revisada con el hash SHA-256 de `cv.md` y el número de rondas. Si el contenido cambia después, reabrí la revisión de lo afectado y actualizá el hash.

El filtro aprueba cuando cada bullet tiene una contribución identificable para ese lector, cada detalle destacado tiene función probatoria y no quedan objeciones materiales abiertas. Aprobar no implica cumplir todos los requisitos de la JD: las brechas reales siguen visibles en la auditoría.
