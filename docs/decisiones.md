# Decisiones

Registro breve de por qué el toolkit es como es. Una entrada por decisión, la más reciente arriba.

## 2026-11-23 — Adaptador para ai-mllc

**Decisión:** sumar `adapters/mllc/` con un catálogo de golden rules por dominio (`golden-rules/ml-foundations.md`) y `compose.py`, que los junta y valida en el formato que exige el núcleo de ai-mllc.

**Por qué:** ai-mllc conduce el proceso y bloquea el cierre de una etapa ante una regla bloqueante, pero no trae reglas propias. El toolkit tiene las reglas y los chequeos. Son capas complementarias: el toolkit no se fusiona con ai-mllc ni depende de él.

**Cómo:** cada regla declara fuerza, etapa, mecanismo y estado. Las de mecanismo `check_determinista` nombran el script de `checks/` y su código de salida se traduce a cumple / no cumple. El catálogo absorbe las tres reglas de referencia que siembra ai-mllc. `compose.py` no pisa un catálogo existente sin `--force`, igual que ai-mllc. Se validó contra el parser real de ai-mllc (0.1.0a1).

**Pendiente:** catálogos de `credit-scoring` y `collections`.

## 2026-11-23 — Prioridades A del relevamiento de repos del equipo

**Decisión:** incorporar a `ml-foundations` lo de prioridad alta del relevamiento de tres años de repos, skills y documentación del equipo: el gate "¿hace falta ML?", uso y respaldo del modelo, demora entre predicción y acción, perfil del target, la etapa de dataset (`03b-dataset.md`), selección sin target vs. predictiva, leaderboard, incertidumbre de métricas, diagnóstico antes de tunear, referencia correcta y gate de entradas en monitoreo, y la ficha de impacto. Dos chequeos nuevos (`target_profile.py`, `check_dataset.py`) y tres plantillas (contrato del dataset, leaderboard, ficha de impacto).

**Dos cambios de criterio respecto de la versión anterior:**

- **Entidades vistas en la validación final:** antes se excluían. Ahora se reporta la validación completa y sin entidades vistas, y el árbitro se elige según la población de predicción. Excluir siempre medía la generalización a entidades nuevas pero no el desempeño real. `check_universe.py` suma `--arbiter-overlap` para no fallar por entidades compartidas solo con la validación final.
- **Test como conjunto de selección:** si el test se usa para early stopping, elegir trials, elegir variables o calibrar, se rotula así y su métrica no se reporta como desempeño. La ficha del modelo lo distingue.

**Además:** la penalización por sobreajuste usa `max(0, train − val)` en lugar del valor absoluto, y la regla de promoción aclara que "mejora mayor que cero" no alcanza.

## 2026-11-23 — Separar lo genérico de ML en `ml-foundations`

**Decisión:** crear el dominio `ml-foundations` con las prácticas de ML supervisado que no dependen del dominio (universo y particiones, leakage, features, modelado, población y sesgo, monitoreo, experimentación, trazabilidad, documentación), los chequeos genéricos y plantillas genéricas, más la skill `ml-practices`. `credit-scoring` queda solo con lo específico de crédito y cada archivo apunta al general que aplica.

**Por qué:** más de la mitad de lo que estaba en `credit-scoring` era ML genérico con ejemplos de crédito. Separarlo permite usarlo en cualquier proyecto y evita duplicarlo en cada dominio nuevo.

**Cómo se apilan:** `credit-scoring` se apoya en `ml-foundations`; `collections` en ambos. Las referencias entre dominios usan la forma `<dominio>/knowledge/<archivo>`, y las skills enlazan dominios completos para que esas rutas funcionen igual dentro de la skill.

**Chequeos:** los cuatro scripts pasan a `ml-foundations/checks/`. `check_leakage.py` es el motor genérico; cada dominio aporta su lista de patrones (`credit-scoring/checks/forbidden_columns.example.txt`).

**No se separó en otro repo:** un dominio dentro del toolkit evita que credit-scoring dependa de un repositorio externo y mantiene una sola instalación.

## 2026-11-23 — Ampliación de la metodología y dominio de cobranzas

**Decisión:** ampliar seis archivos de conocimiento de credit-scoring, sumar ratings, experimentación y trazabilidad, crear el dominio `collections`, sumar `shared/knowledge/agent-workflow.md` y dos chequeos nuevos (`check_universe.py`, `check_concentration.py`).

**Por qué:** son prácticas probadas en modelos productivos y complementan la metodología inicial, que era más genérica. Algunas quedaron como reglas explícitas porque son errores frecuentes: margen mínimo para reemplazar un modelo, árbitro intacto, recalibrar después de rebalancear y documentación verificada contra el código.

**Criterio:** el toolkit solo contiene prácticas en términos generales. Ningún código, nombre de tabla, sistema, monto ni persona de una organización.

**Regla central de cobranzas:** el modelo se entrena y se evalúa solo con el grupo de control.

## 2026-11-23 — Instalación en `~/.agents/skills/`

**Decisión:** reemplazar `install-claude.sh` por `install.sh`, que enlaza cada skill en `~/.agents/skills/` y desde ahí en la carpeta de cada herramienta.

**Por qué:** es un patrón probado para compartir skills entre herramientas y encaja con el principio de que el contenido es neutral a la herramienta. Agregar una herramienta nueva es una línea.

## 2026-11-23 — Nombres de dominios

**Decisión:** `collections` en inglés, como `credit-scoring`; `productividad` queda en español porque así lo eligió la usuaria. El contenido de todos los dominios está en español.

## 2026-11-23 — Dominio productividad y cv-con-evidencia

**Decisión:** mover la skill `cv-con-evidencia` (antes suelta en `~/projects/skills/`) a `domains/productividad/`, tal como estaba.

**Por qué:** juntar todas las herramientas en un solo repo versionado. No se separó en `knowledge/`, `checks/` y `templates/` porque ya funcionaba como skill autocontenida; se reorganiza solo si hace falta usarla desde otra herramienta.

**Además:** se descartó la skill vieja `scoring-strategy-crediticio`, que nunca se terminó. `credit-scoring-ml` la reemplaza.

## 2026-11-23 — Estructura inicial

**Decisión:** separar contenido neutral (`domains/`, `shared/`) de adaptadores por herramienta (`adapters/`).

**Por qué:** el conocimiento y los chequeos son lo que perdura; las herramientas y los modelos cambian. Si mañana uso otra herramienta, solo reescribo un adaptador.

**Consecuencia:** el adaptador de Claude usa enlaces simbólicos hacia `domains/` para no duplicar archivos. El de Cursor resume las reglas y referencia los archivos de conocimiento.

## 2026-11-23 — Guardrails en scripts, no solo en texto

**Decisión:** toda regla que no se puede romper tiene un chequeo en `checks/` que sale con código de error.

**Por qué:** un modelo puede ignorar u olvidar una instrucción; un script que falla no. Esto además hace que el toolkit funcione igual con modelos que siguen instrucciones con menos rigor.

## 2026-11-23 — Primer dominio: credit-scoring

**Decisión:** arrancar con scoring de riesgo crediticio (originación de personas, con extensión a PyMEs).

**Por qué:** es el dominio donde más se repite el trabajo y donde los errores metodológicos (leakage, validación aleatoria, mala definición de default) son más caros.
