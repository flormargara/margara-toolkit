# Decisiones

Registro breve de por qué el toolkit es como es. Una entrada por decisión, la más reciente arriba.

## 2026-11-26 — Prioridades B del relevamiento

**Decisión:** sumar `promotion.py` a `ml-foundations/checks/`, `scripts/lint_skills.py` con sus tests, la plantilla `discovery.md`, métricas de negocio por banda (07), cadena de consumo (08), estándar de Python y cambios después de producción (09), y en `shared/` el diagnóstico con cadena de evidencia y la revisión adversarial de skills por perfil de riesgo.

**`promotion.py` decide, no falla:** sale con 0 y devuelve champion, recalibrado o challenger; con datos insuficientes se queda el champion, como dice la regla. Por eso la regla `ml-regla-de-promocion` del catálogo de ai-mllc sigue como atestación y usa la salida del script como evidencia, sin cambiar de versión. Mide orden con AUC y calibración por deciles porque son comunes a cualquier clasificador binario; un dominio con otra métrica principal la compara aparte.

**Margen o intervalo:** por defecto alcanza con uno de los dos, como en `06-monitoreo.md`; `--require both` exige ambos. El bootstrap es pareado (las mismas filas para los dos modelos), porque la diferencia entre modelos sobre la misma cohorte varía mucho menos que cada AUC por separado.

**El lint corre en los tests:** `tests/test_toolkit.py` lo corre sobre el repo real, así una referencia rota se nota antes de commitear. Respeta dos convenciones del toolkit: los chequeos se nombran sin carpeta y los archivos de cada proyecto (`forbidden_columns.txt`, nombres en mayúsculas) no se buscan en el repo.

**Ya estaban:** "reentrenar o versión nueva" (06) y las señales de alarma del discovery (00).

## 2026-11-26 — Prioridades M del relevamiento que eran texto

**Decisión:** sumar `templates/modeling-spec.md`, el ancla entre documentación y código y el estándar de SQL en `09-documentacion.md`, y en `shared/knowledge/agent-workflow.md` la revisión en dos niveles y cómo escribir skills.

**Por qué:** la spec se nombraba como `MODELING_SPEC.md` en los archivos de memoria del proyecto, pero no tenía plantilla. El ancla vuelve detectable la documentación desactualizada sin releerla entera: el commit revisado se compara con el último que tocó el código.

**Diferencia con el relevamiento:** proponía la `description` de las skills en inglés. Se descartó porque las del toolkit están en español, que es el idioma en que se piden las tareas; la regla quedó como "en el idioma en que se piden".

**Pendiente de esa prioridad:** `check_inputs.py`, que se hace cuando un proyecto real tenga un contrato de tablas para probarlo.

## 2026-11-26 — Golden rules de crédito y cobranzas

**Decisión:** sumar `golden-rules/credit-scoring.md` (20 reglas, prefijo `cr-`) y `golden-rules/collections.md` (13, `co-`). Se componen después de `ml-foundations` y solo agregan lo propio del dominio.

**Por qué:** las reglas generales ya cubren particiones, leakage, baselines o grupo de control; repetirlas duplicaría evaluaciones. Las de dominio suman lo que no está en lo general: roll rate y componentes del target, WoE, PD y ratings, punto de corte del dueño del riesgo, entrenar solo con control y gestiones del episodio actual.

**Cómo:** el binning WoE va en la etapa `model` y no en `features`, porque mira el target y en `features` rige la selección sin target. Las reglas que no siempre corresponden (PD como número, ratings, auditoría de equidad) dicen cuándo son `no_aplica`. `tests/test_mllc_catalogs.py` verifica que los comandos de las reglas existan con esos flags.

## 2026-11-25 — ai-mllc como repo propio, con adaptador para Claude Code

**Decisión:** ai-mllc vive en `~/projects/ai-mllc`, separado del toolkit, importado desde la copia del repo del equipo. Ahí se sumó `adapters/claude/`. El toolkit conserva solo `adapters/mllc/` (catálogo de golden rules y `compose.py`).

**Por qué:** ai-mllc es otra herramienta (proceso, estado, etapas); el toolkit es criterio. El adaptador de una herramienta para Claude Code pertenece a esa herramienta, no al toolkit. El equipo y el repo original ya no existen, así que se mantiene como repo propio y privado.

## 2026-11-25 — Se saca el dominio productividad

**Decisión:** quitar `domains/productividad/cv-con-evidencia` y su skill del catálogo, por ahora.

**Por qué:** el toolkit se concentra en ML y crédito. La skill queda en el historial de git; para recuperarla: `git checkout 91bcc38 -- domains/productividad adapters/claude/skills/cv-con-evidencia`.

## 2026-11-23 — Tests de los chequeos

**Decisión:** sumar `tests/` con `unittest`, un archivo por dominio, que corre cada chequeo como un usuario (subproceso) y verifica el código de salida y el mensaje.

**Por qué:** los chequeos son la garantía del toolkit; si un cambio rompe uno, tiene que notarse antes de usarlo en un proyecto. Se prueba el contrato de línea de comandos y no las funciones internas, para poder reescribir un script sin reescribir sus tests.

**Sin dependencias:** `unittest` en lugar de `pytest`, porque los chequeos corren con la biblioteca estándar y los tests también tienen que correr en cualquier entorno. Los datos sintéticos se generan con semilla fija dentro de cada test; ningún dato real entra al repo.

## 2026-11-23 — Chequeos propios de crédito y cobranzas

**Decisión:** sumar tres chequeos a `credit-scoring/checks/` (`roll_rate.py`, `check_woe_bins.py`, `check_ratings.py`) y dos a `collections/checks/` (`check_training_population.py`, `check_control_group.py`).

**Por qué:** las reglas centrales de esos dominios (default justificado con roll rate, binning monótono, ratings calibrados, entrenar solo con control) estaban solo en texto. Siguiendo el principio de que lo crítico se verifica con scripts, ahora fallan con error.

**Entradas neutrales:** cada chequeo lee un CSV con columnas configurables (historia mensual de atrasos, tabla de binning, muestra puntuada, registro de asignaciones), no la salida de una librería concreta.

**Qué falla y qué advierte:** falla lo que invalida el resultado (bins con WoE infinito, ratings no monótonos o fuera de tolerancia, cortes superpuestos, filas tratadas en el entrenamiento, control que cambia de grupo). Advierte lo que requiere juicio (bandas que podrían unirse, tramo indeterminado, cohortes inestables). Las excepciones justificadas se declaran con flags explícitos (`--allow-nonmonotonic`, `--allow-high-iv`).

**Proporción del control por cuenta, no por fila:** con un control persistente la misma cuenta aparece en muchas corridas; contar filas subestima el desvío binomial y falla por ruido.

**`check_ratings.py` vive en crédito:** los ratings son de ese dominio; cobranzas lo usa con `--where grupo=control`. En la skill `credit-scoring-ml`, el enlace `patterns/` pasa a llamarse `checks/` porque ya no contiene solo la lista de patrones.

## 2026-11-23 — Adaptador para ai-mllc

**Decisión:** sumar `adapters/mllc/` con un catálogo de golden rules por dominio (`golden-rules/ml-foundations.md`) y `compose.py`, que los junta y valida en el formato que exige el núcleo de ai-mllc.

**Por qué:** ai-mllc conduce el proceso y bloquea el cierre de una etapa ante una regla bloqueante, pero no trae reglas propias. El toolkit tiene las reglas y los chequeos. Son capas complementarias: el toolkit no se fusiona con ai-mllc ni depende de él.

**Cómo:** cada regla declara fuerza, etapa, mecanismo y estado. Las de mecanismo `check_determinista` nombran el script de `checks/` y su código de salida se traduce a cumple / no cumple. El catálogo absorbe las tres reglas de referencia que siembra ai-mllc. `compose.py` no pisa un catálogo existente sin `--force`, igual que ai-mllc. Se validó contra el parser real de ai-mllc (0.1.0a1).

**Catálogos de dominio:** ver la entrada del 2026-11-26.

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
