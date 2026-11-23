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
  mllc/         catálogo de golden rules para ai-mllc
  AGENTS.md     punto de entrada común para cualquier herramienta
scripts/        instalación y utilidades del propio toolkit
docs/           decisiones y su porqué
```

## Índice

| Dominio | Pieza | Qué hace | Cuándo usarla |
|---|---|---|---|
| ml-foundations | `knowledge/` | Prácticas de ML supervisado con datos en el tiempo, en 11 etapas: ¿hace falta ML? y problem framing, universo y particiones, leakage, features, dataset, modelado, población y sesgo, monitoreo, experimentación e impacto, trazabilidad y documentación | En cualquier proyecto de modelado |
| ml-foundations | `checks/target_profile.py` | Perfil del target por período: volumen, tasa, tendencia, saltos de régimen y veredicto viable / parcial / descartado | Antes de definir cortes y particiones |
| ml-foundations | `checks/check_universe.py` | Integridad temporal del universo: orden, horizonte, madurez, entidades repetidas, duplicados | Antes de entrenar |
| ml-foundations | `checks/check_dataset.py` | Gate del dataset: duplicados de grano, filas y target preservados contra el universo, superposición temporal, faltantes, esquema idéntico entre train, validación y scoring | Antes de modelar |
| ml-foundations | `checks/check_leakage.py` | Detecta columnas prohibidas en código o listas de features (la lista de patrones la pone cada dominio) | Hook después de editar código, y antes de reportar métricas |
| ml-foundations | `checks/check_concentration.py` | Concentración de la importancia (top-1, top-3, número efectivo de variables) | Al aceptar un modelo |
| ml-foundations | `checks/psi.py` | PSI/CSI entre dos muestras | Validación y monitoreo |
| ml-foundations | `templates/` | Ficha del modelo y checklist de validación genéricas; contrato del dataset, leaderboard y ficha de impacto | Durante el modelado, al cerrar el modelo y antes del despliegue |
| adapters | `mllc/` | Genera el catálogo de golden rules de ai-mllc desde los dominios del toolkit (`compose.py`) y explica cómo usar las skills del toolkit como soporte | En proyectos que usan ai-mllc |
| credit-scoring | `knowledge/` | Lo específico de scores de riesgo: default y roll rate, ventana de desempeño, WoE/IV, PD y puntos, punto de corte, reject inference, ratings, equidad, bandas de prueba y límites, trazabilidad evaluación → desempeño | Al construir o monitorear un score |
| credit-scoring | `checks/forbidden_columns.example.txt` | Patrones de leakage de crédito y cobranzas | Al armar el `forbidden_columns.txt` de un proyecto de crédito |
| credit-scoring | `checks/roll_rate.py` | Matriz de transición y peor tramo → default; con `--bad-from` verifica la definición de malo propuesta | Al definir el evento de default |
| credit-scoring | `checks/check_woe_bins.py` | Tabla de binning: bins sin una clase, tamaño y malos mínimos, monotonía del WoE, IV fuera de rango | Antes de la regresión logística sobre WoE |
| credit-scoring | `checks/check_ratings.py` | Escala de ratings: monotonía, tamaño mínimo, calibración por rating, cortes sin superposición, separación y estabilidad por cohorte | Al verificar los cortes en OOT y en el monitoreo |
| credit-scoring | `templates/` | Ficha y checklist de crédito (extienden las genéricas) | Antes de dar un score por terminado |
| collections | `knowledge/` | Modelos de cobranzas: problem framing, entrenamiento solo con grupo de control, target de pase de tramo y autocura, leakage propio, métricas de impacto y costo | Al construir o revisar un modelo de mora o cobranzas |
| collections | `checks/check_training_population.py` | Entrenamiento y evaluación solo con control desde el inicio del modelo; autocura solo sin gestión | Antes de entrenar o reentrenar |
| collections | `checks/check_control_group.py` | Control persistente, proporción por rating y tamaño suficiente para reentrenar | Al diseñar el piloto y en cada reentrenamiento |
| collections | `templates/problem-framing.md` | Problem framing para acordar con cobranzas | Al empezar un modelo de cobranzas |
| productividad | `cv-con-evidencia/` | Base personal de experiencia confirmada; CVs adaptados a ofertas, auditoría de CVs y textos de postulación | Al armar o actualizar un CV o postularse a un puesto |
| shared | `knowledge/agent-workflow.md` | Memoria del proyecto en archivos, criterios de cierre, `AGENTS.md` para librerías, seguridad de skills | En cualquier proyecto con agentes |

Los dominios se apilan: `credit-scoring` se apoya en `ml-foundations`, y `collections` en ambos. Cada archivo de un dominio específico empieza diciendo qué archivo general aplica.

Skills en `adapters/claude/skills/`: `ml-practices`, `credit-scoring-ml`, `collections-ml` y `cv-con-evidencia`. Todas apuntan con enlaces simbólicos al contenido de `domains/` y `shared/`, así cada archivo existe una sola vez.

## Instalación

```bash
./scripts/install.sh
```

- Enlaza cada skill del catálogo en `~/.agents/skills/` (ubicación común que algunas herramientas leen directamente).
- Desde ahí, enlaza cada skill en la carpeta de cada herramienta que lo necesita (hoy `~/.claude/skills/`). Agregar otra herramienta es agregar una línea en `TOOL_DIRS`.
- Nunca pisa carpetas reales. `./scripts/install.sh --uninstall` quita solo los enlaces que apuntan a este repo.

Los hooks no se instalan solos: copiar el bloque que corresponda de `adapters/claude/settings.example.json` al `settings.json` del proyecto donde se quieran.

## Uso en un proyecto

- **Claude Code:** las skills quedan disponibles en todos los proyectos tras instalarlas. Las reglas de `adapters/claude/rules/` se copian a `.claude/rules/` del proyecto: `ml-guardrails.md` en cualquier proyecto de ML, y además `credit-scoring-guardrails.md` en uno de crédito.
- **Cursor:** copiar a `.cursor/rules/` del proyecto `ml-foundations.mdc` y, si es de crédito, también `credit-scoring.mdc`.
- **Otras herramientas:** apuntar a `adapters/AGENTS.md` o copiarlo como `AGENTS.md` del proyecto.
- **ai-mllc:** generar el catálogo de golden rules con `python3 adapters/mllc/compose.py ml-foundations --out <carpeta de configuración>/mllc-golden-rules.md` (ver `adapters/mllc/README.md`).

## Cómo crece este repo

1. Una herramienta nace dentro de un proyecto concreto y se prueba con datos reales.
2. Si funciona y sirve más allá de ese proyecto, se mueve acá.
3. Un dominio nuevo se crea recién cuando hay dos o tres piezas reales que lo justifican.
4. Lo que se repite entre dominios sube a `shared/`.
5. Si lo usa un equipo, se empaqueta como plugin.

Cada herramienta nueva suma una fila al índice y, si la decisión no es obvia, una entrada en `docs/decisiones.md`.
