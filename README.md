# margara-toolkit

Herramientas personales para trabajar con agentes de IA: conocimiento de dominio, chequeos automáticos y plantillas, independientes de la herramienta (Claude Code, Cursor u otra) y del modelo.

## Principio de diseño

- **El contenido es neutral.** `domains/` y `shared/` contienen Markdown y scripts de Python. Ningún archivo ahí depende de una herramienta.
- **Los adaptadores son delgados.** `adapters/` solo envuelve ese contenido en el formato que cada herramienta espera (skill, regla, hook).
- **Lo crítico se verifica con scripts, no con texto.** Si una regla no se puede romper nunca, tiene un chequeo en `checks/` que falla con error. Así funciona igual con cualquier modelo.

## Estructura

```
domains/<dominio>/
  knowledge/    buenas prácticas y criterios (Markdown)
  checks/       scripts que verifican y fallan con error
  templates/    plantillas de entregables
shared/         lo transversal a varios dominios
adapters/
  claude/       skills, reglas, subagentes y ejemplo de hooks para Claude Code
  cursor/       reglas .mdc para Cursor
  AGENTS.md     punto de entrada común para cualquier herramienta
scripts/        instalación y utilidades del propio toolkit
docs/           decisiones y su porqué
```

## Índice

| Dominio | Pieza | Qué hace | Cuándo usarla |
|---|---|---|---|
| credit-scoring | `knowledge/` | Metodología para scores de riesgo crediticio en 13 etapas: trazabilidad, target, universo, leakage, features, modelado, sesgo de selección, monitoreo, equidad, documentación, ratings y experimentación | Al diseñar, entrenar, validar, desplegar o monitorear un score |
| credit-scoring | `checks/check_universe.py` | Integridad temporal del universo: orden, horizonte, madurez, entidades repetidas, duplicados | Antes de entrenar |
| credit-scoring | `checks/check_leakage.py` | Detecta columnas prohibidas (posteriores a la decisión) en código o listas de features | Hook después de editar código, y antes de reportar métricas |
| credit-scoring | `checks/check_concentration.py` | Concentración de la importancia (top-1, top-3, número efectivo de variables) | Al aceptar un modelo |
| credit-scoring | `checks/psi.py` | PSI/CSI entre dos muestras | Validación out-of-time y monitoreo |
| credit-scoring | `templates/` | Checklist de validación y ficha del modelo | Antes de dar un modelo por terminado |
| collections | `knowledge/` | Modelos de cobranzas: problem framing, entrenamiento solo con grupo de control, target de pase de tramo y autocura, leakage propio, métricas de impacto y costo | Al construir o revisar un modelo de mora o cobranzas |
| collections | `templates/problem-framing.md` | Problem framing para acordar con cobranzas | Al empezar un modelo de cobranzas |
| productividad | `cv-con-evidencia/` | Base personal de experiencia confirmada; CVs adaptados a ofertas, auditoría de CVs y textos de postulación | Al armar o actualizar un CV o postularse a un puesto |
| shared | `knowledge/agent-workflow.md` | Memoria del proyecto en archivos, criterios de cierre, `AGENTS.md` para librerías, seguridad de skills | En cualquier proyecto con agentes |

Skills en `adapters/claude/skills/`: `credit-scoring-ml`, `collections-ml` y `cv-con-evidencia`. Todas apuntan con enlaces simbólicos al contenido de `domains/` y `shared/`, así cada archivo existe una sola vez.

## Instalación

```bash
./scripts/install.sh
```

- Enlaza cada skill del catálogo en `~/.agents/skills/` (ubicación común que algunas herramientas leen directamente).
- Desde ahí, enlaza cada skill en la carpeta de cada herramienta que lo necesita (hoy `~/.claude/skills/`). Agregar otra herramienta es agregar una línea en `TOOL_DIRS`.
- Nunca pisa carpetas reales. `./scripts/install.sh --uninstall` quita solo los enlaces que apuntan a este repo.

Los hooks no se instalan solos: copiar el bloque que corresponda de `adapters/claude/settings.example.json` al `settings.json` del proyecto donde se quieran.

## Uso en un proyecto

- **Claude Code:** las skills quedan disponibles en todos los proyectos tras instalarlas. La regla `adapters/claude/rules/credit-scoring-guardrails.md` se copia a `.claude/rules/` del proyecto.
- **Cursor:** copiar `adapters/cursor/rules/*.mdc` a `.cursor/rules/` del proyecto.
- **Otras herramientas:** apuntar a `adapters/AGENTS.md` o copiarlo como `AGENTS.md` del proyecto.

## Cómo crece este repo

1. Una herramienta nace dentro de un proyecto concreto y se prueba con datos reales.
2. Si funciona y sirve más allá de ese proyecto, se mueve acá.
3. Un dominio nuevo se crea recién cuando hay dos o tres piezas reales que lo justifican.
4. Lo que se repite entre dominios sube a `shared/`.
5. Si lo usa un equipo, se empaqueta como plugin.

Cada herramienta nueva suma una fila al índice y, si la decisión no es obvia, una entrada en `docs/decisiones.md`.
