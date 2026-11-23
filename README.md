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
| credit-scoring | `knowledge/` | Metodología para construir scores de riesgo crediticio | Al diseñar, entrenar, validar o documentar un score |
| credit-scoring | `checks/check_leakage.py` | Detecta columnas prohibidas (posteriores a la decisión) en código o listas de features | Hook después de editar código de modelado, o en CI |
| credit-scoring | `checks/psi.py` | Calcula PSI/CSI entre dos muestras | Validación out-of-time y monitoreo |
| credit-scoring | `templates/` | Checklist de validación y ficha del modelo | Antes de dar un modelo por terminado |
| productividad | `cv-con-evidencia/` | Base personal de experiencia confirmada; CVs adaptados a ofertas, auditoría de CVs y textos de postulación | Al armar o actualizar un CV o postularse a un puesto |

Las skills de Claude están en `adapters/claude/skills/`: `credit-scoring-ml` y `cv-con-evidencia` (esta última es un enlace a `domains/productividad/cv-con-evidencia`, que ya trae su propio formato de skill).

## Instalación en Claude Code

```bash
./scripts/install-claude.sh
```

Crea enlaces simbólicos desde `~/.claude/skills/` hacia las skills de este repo. Los hooks no se instalan solos: copiá el bloque que corresponda de `adapters/claude/settings.example.json` al `settings.json` del proyecto donde los quieras.

## Uso en un proyecto

- **Claude Code:** la skill queda disponible en todos los proyectos tras instalarla. La regla `adapters/claude/rules/credit-scoring-guardrails.md` se copia a `.claude/rules/` del proyecto.
- **Cursor:** copiar `adapters/cursor/rules/*.mdc` a `.cursor/rules/` del proyecto.
- **Otras herramientas:** apuntar a `adapters/AGENTS.md` o copiarlo como `AGENTS.md` del proyecto.

## Cómo crece este repo

1. Una herramienta nace dentro de un proyecto concreto y se prueba con datos reales.
2. Si funciona y sirve más allá de ese proyecto, se mueve acá.
3. Un dominio nuevo se crea recién cuando hay dos o tres piezas reales que lo justifican.
4. Lo que se repite entre dominios sube a `shared/`.
5. Si lo usa un equipo, se empaqueta como plugin.

Cada herramienta nueva suma una fila al índice y, si la decisión no es obvia, una entrada en `docs/decisiones.md`.
