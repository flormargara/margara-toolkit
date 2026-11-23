# Decisiones

Registro breve de por qué el toolkit es como es. Una entrada por decisión, la más reciente arriba.

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
