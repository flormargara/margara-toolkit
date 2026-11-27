# Discovery — [proyecto]

Se completa con quien pide el modelo **antes del problem framing** (ver `knowledge/00-flujo.md`). Vive en el proyecto como `DISCOVERY_LOG.md`. Cada respuesta lleva su estado: explícita, candidata, confirmada, desconocida o contradicha.

| Campo | Valor |
|---|---|
| Quién pide | |
| Sponsor con poder de decisión | |
| Fecha | |

## 1. ¿Hace falta ML?

Si alguna respuesta es "no", el proyecto es otro y se dice acá.

| Pregunta | Respuesta | Si es "no" |
|---|---|---|
| ¿Hay una decisión periódica y repetible que dependa de información disponible? | | Analítica o tablero |
| ¿Una regla simple ya captura el valor? (estimar el valor incremental de un modelo sobre ella, no la cobertura) | | Regla con monitoreo |
| ¿Hay un target histórico con calidad razonable? | | Instrumentar captura y trazabilidad primero |

Veredicto: ✅ sigue a problem framing · ❌ no es un proyecto de ML · ⚠️ falta información (qué y quién la trae)

## 2. Preguntas

| Tema | Qué buscamos | Qué pedir | Señal de alarma |
|---|---|---|---|
| Problema | Magnitud y evolución en números | Serie histórica del indicador, costo actual | El problema no tiene números |
| Decisión | Qué se decide, quién y cada cuánto | Descripción del proceso actual, ejemplos de casos reales | No hay proceso actual ni responsable |
| Proceso vigente | Cómo se decide hoy y con qué criterio | Reglas, planillas, registros de decisiones | "Lo decide la experiencia" y nadie quiere contrastarlo |
| Éxito | Una métrica de negocio con dirección y umbral | El objetivo del área donde aparece el proyecto | No logran elegir una sola métrica; no está en los objetivos del área |
| Datos | Fuentes, historia disponible, quién las mantiene | Acceso, diccionario, ejemplos de registros | Nadie sabe qué significa una columna clave |
| Trazabilidad | Se puede unir predicción, decisión y resultado | Una consulta de ejemplo que una los tres | Las decisiones no quedan registradas |
| Uso | Quién consume la salida, cómo y cuándo | Sistema destino, formato, frecuencia, latencia | No hay quién lo integre ni lo mantenga |
| Respaldo | Qué pasa si el modelo no está | Proceso alternativo | "Si falla, se para todo" sin plan |
| Impacto | Contra qué se va a comparar | Posibilidad de un grupo de control | No se acepta ningún control ni línea base |

## 3. Hallazgos

Se agrega, no se sobrescribe.

| Fecha | Hallazgo | Fuente | Estado |
|---|---|---|---|
| | | | |

## 4. Pendientes y próxima actividad

- Qué falta confirmar y quién lo confirma:
- Siguiente actividad que produce evidencia:
