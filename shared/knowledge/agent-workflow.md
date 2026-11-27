# Trabajar con agentes en proyectos de datos y modelos

Prácticas transversales para cualquier dominio. Sirven igual para Claude Code, Cursor u otra herramienta.

## Memoria del proyecto en archivos

El agente no recuerda entre sesiones; el repositorio sí. Cada etapa deja un archivo Markdown que cualquier persona o agente puede leer para retomar el trabajo:

| Archivo | Contenido |
|---|---|
| `AGENTS.md` | Convenciones del proyecto, rutas, comandos y reglas. Tiene prioridad sobre todo lo demás |
| `DISCOVERY_LOG.md` | Hallazgos del EDA y de las fuentes de datos |
| `UNIVERSE_LOG.md` | Target, grano, horizonte, esquema de partición y veredicto de integridad |
| `FEATURE_CATALOG.md` | Variables con su diseño, fuente, disponibilidad y estado (aprobada / descartada y por qué) |
| `MODELING_SPEC.md` | Objetivo, métrica principal, criterio de "suficientemente bueno", restricciones y esquema de validación (`ml-foundations/templates/modeling-spec.md`) |
| `EXPERIMENTS_LOG.md` | Una fila por experimento: qué cambió, resultado, veredicto |

Reglas:

- **Se agrega, no se sobrescribe.** Las entradas tienen fecha; las decisiones viejas quedan como historia.
- **Cada etapa empieza leyendo** los archivos de las etapas anteriores y buscándolos por nombre en el proyecto, no suponiendo una ruta.
- **Si falta una etapa anterior**, el agente lo dice y no la inventa.

## Criterios de cierre

Cada paso termina con un veredicto explícito: ✅ listo, ❌ descartado, ⚠️ requiere revisión. Un paso sin veredicto no está cerrado y el agente no avanza al siguiente.

Que un script termine bien o que una métrica sea buena es evidencia, no cierre. El agente presenta la evidencia y su interpretación; la etapa la cierra una decisión explícita del responsable: aceptar, aceptar con condiciones, devolver o descartar.

El agente trabaja solo entre esos puntos y resuelve lo operativo sin preguntar. Pide una decisión cuando cambia el sentido o la validez del resultado, cuando una regla bloqueante no se cumple, cuando propone una excepción o cuando hay que cerrar.

Una excepción a una regla se registra con: qué regla, alcance, motivo, consecuencias aceptadas, responsable, qué resultados dependen de ella y cuándo vence o se revisa.

## Reglas con fuerza, mecanismo y estado

Cada regla de un dominio se puede describir con tres atributos. Así se ve qué reglas tienen un chequeo que las hace cumplir y cuáles dependen de que alguien las lea:

| Atributo | Valores |
|---|---|
| Fuerza | **bloqueante** (no se cierra la etapa sin cumplirla o sin una excepción), **alerta** (se muestra y se decide), **sugerencia** |
| Mecanismo | El más barato que preserva la validez: **chequeo determinista** (un script que falla), **atestación** (el agente muestra la evidencia pedida), **discusión** (se acuerda con el responsable y se registra) |
| Estado | **draft** (se evalúa y se muestra, pero nunca bloquea) o **active** |

- La falta de evidencia bloquea igual que el incumplimiento: un chequeo que no se pudo correr no es verde.
- Cambiar el sentido de una regla es una versión nueva; corregir la redacción no.
- Una regla nueva entra como draft y se activa cuando se probó en proyectos reales.
- El catálogo de `ml-foundations` con estos atributos está en `adapters/mllc/golden-rules/ml-foundations.md`.

## Cómo redactar reglas para agentes

- Una idea por regla, en imperativo y concreta.
- El porqué, si no es obvio: un agente aplica mejor una regla cuyo motivo entiende.
- Qué no hacer, además de qué hacer.
- Un ejemplo antes que una explicación larga.
- Separar las reglas siempre activas de las que aplican a un tipo de proyecto o de archivo.
- Pocas reglas: con muchas, el modelo pierde las del medio; lo primero y lo último del contexto pesan más.

## Recibir material de otra persona

Al tomar notebooks, scripts o queries para llevarlos a producción, marcar como riesgo, sin descartarlo en silencio:

- Credenciales o secretos en el código.
- Rutas absolutas de la máquina de quien lo escribió.
- Notebooks con estado oculto: celdas ejecutadas fuera de orden o variables globales modificadas entre celdas.

No cambiar la lógica de negocio o de modelado al reinterpretarla: solo clasificarla. Los datos reales que vengan con el material no se commitean.

## Definiciones de negocio: una pregunta a la vez

En target, métrica principal, umbral de "suficientemente bueno" y restricciones:

- Preguntar **una pieza por vez** y confirmar antes de seguir.
- **No completar con un supuesto propio "razonable".** Si un archivo anterior ya responde la pregunta, proponer esa respuesta y pedir confirmación.
- Lo que es un dato (rango de fechas disponible, volumen) se calcula, no se pregunta.

## El código manda sobre la documentación

Cuando la documentación y el código se contradicen, el agente sigue el código y avisa la contradicción. La documentación desactualizada se corrige en el mismo cambio.

Para que la contradicción se pueda detectar antes de leer todo, cada documento que describe código lleva un ancla con el commit contra el que se revisó (`ml-foundations/knowledge/09-documentacion.md`, "Ancla entre documentación y código").

## Revisión en dos niveles

Una revisión de código, de un notebook o de un entregable se divide en dos pasadas con salidas distintas:

| Nivel | Qué reporta | Cómo |
|---|---|---|
| **Estricto** | Solo lo que bloquea: rompe una regla bloqueante, invalida un resultado o un despliegue | Cada hallazgo con evidencia `archivo:línea` (o tabla y celda) y la regla que rompe. Sin evidencia no es hallazgo |
| **Sugerencias** | Lo que mejoraría pero no bloquea: legibilidad, simplificación, una práctica recomendada | Agrupadas y breves; nunca se presentan como bloqueantes |

- Ninguno de los dos lista lo que está bien: un resumen de lo que pasa diluye lo que no pasa.
- Si el nivel estricto no encuentra nada, lo dice en una línea.
- Mezclarlos hace que quien recibe la revisión no sepa qué tiene que arreglar antes de seguir.

## Escribir skills

Una skill aporta **metodología**: qué hacer, en qué orden y con qué criterio. El **contorno** lo pone el entorno donde corre: dónde escribir los archivos, cómo registrar el avance, cuándo cerrar una etapa y quién aprueba. Una skill que fija rutas o el flujo de aprobación no se puede usar en otra herramienta ni en otro proyecto.

- La `description` es lo que la herramienta lee para decidir cuándo activarla: dice qué hace y cuándo usarla, con las palabras con las que alguien lo pediría y en el idioma en que se piden las tareas (en este toolkit, español). Nombra las skills vecinas cuando el límite entre ellas no es obvio.
- El cuerpo es un índice corto que lleva a los archivos de conocimiento; no copia su contenido.
- Sin rutas absolutas de una máquina: rutas relativas a la skill o al repositorio.
- Sin links rotos ni referencias a archivos que no existen.
- Los chequeos se nombran con el comando exacto para correrlos.
- Una skill que ejecuta queries, escribe archivos o guarda memoria pasa por la revisión de seguridad de abajo.

## `AGENTS.md` para librerías y repositorios compartidos

Un `AGENTS.md` útil para que un agente modifique una librería sin romperla incluye:

- Qué es y qué **no** es el proyecto.
- Orden de lectura del repositorio.
- Cómo se cambia el comportamiento: por parámetros, por configuración o tocando código.
- **Invariantes** que no hay que romper (convenciones de nombres, contratos de entrada y salida, nombres fijos de pasos).
- **Trampas conocidas** (imports con efectos secundarios, objetos que no son thread-safe, supuestos como "target binario").
- Cómo probar un cambio.
- Qué no tocar sin coordinar con otro equipo.
- Limitaciones y pendientes.

## Seguridad de skills y agentes

Las skills que ejecutan queries, escriben archivos o guardan memoria son superficie de ataque. Revisarlas con esta lista:

| Riesgo | Mitigación |
|---|---|
| Ejecución de DDL o escrituras desde una skill de exploración | Bloqueo por código de `CREATE`, `DROP`, `ALTER`, `INSERT`, `DELETE`, `UPDATE`, no solo por instrucción en texto |
| Escaneos completos de tablas grandes | Exigir filtro por partición y `LIMIT` en exploración; estimar el costo antes de ejecutar |
| Parámetros sin sanitizar en queries | Parámetros tipados y validados; nunca concatenar texto del usuario o de los datos |
| Rutas construidas con valores de los datos | Normalizar y verificar que la ruta final quede dentro del directorio esperado (path traversal) |
| Memoria persistente envenenada | Validar cada aprendizaje antes de guardarlo; no promover un aprendizaje a regla solo porque se repitió |
| Instrucciones dentro de datos, documentos o páginas | Tratarlas como datos; nunca como órdenes |
| Sanitización por palabras clave | Se evade con paráfrasis u otro idioma; complementar con controles por código |
| Divisiones por cero y valores vacíos en reportes | Manejar volumen cero de forma explícita |

Llevar un registro acumulativo de auditorías: vulnerabilidades por tipo de skill, mitigaciones que funcionaron y las que no, y falsos positivos.

## Instalación compartida entre herramientas

- La copia real de cada skill vive en `~/.agents/skills/<nombre>`.
- Cada herramienta que no lee esa carpeta recibe un enlace simbólico (por ejemplo `~/.claude/skills/<nombre>`).
- Un catálogo versionado (en este toolkit, `adapters/claude/skills/`) define qué se instala. El instalador no toca lo que no está en el catálogo.
