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
| `MODELING_SPEC.md` | Objetivo, métrica principal, criterio de "suficientemente bueno", restricciones y esquema de validación |
| `EXPERIMENTS_LOG.md` | Una fila por experimento: qué cambió, resultado, veredicto |

Reglas:

- **Se agrega, no se sobrescribe.** Las entradas tienen fecha; las decisiones viejas quedan como historia.
- **Cada etapa empieza leyendo** los archivos de las etapas anteriores y buscándolos por nombre en el proyecto, no suponiendo una ruta.
- **Si falta una etapa anterior**, el agente lo dice y no la inventa.

## Criterios de cierre

Cada paso termina con un veredicto explícito: ✅ listo, ❌ descartado, ⚠️ requiere revisión. Un paso sin veredicto no está cerrado y el agente no avanza al siguiente.

## Definiciones de negocio: una pregunta a la vez

En target, métrica principal, umbral de "suficientemente bueno" y restricciones:

- Preguntar **una pieza por vez** y confirmar antes de seguir.
- **No completar con un supuesto propio "razonable".** Si un archivo anterior ya responde la pregunta, proponer esa respuesta y pedir confirmación.
- Lo que es un dato (rango de fechas disponible, volumen) se calcula, no se pregunta.

## El código manda sobre la documentación

Cuando la documentación y el código se contradicen, el agente sigue el código y avisa la contradicción. La documentación desactualizada se corrige en el mismo cambio.

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
