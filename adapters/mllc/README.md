# Adaptador para ai-mllc

ai-mllc (`~/projects/ai-mllc`, repo propio desde que el equipo que lo armó dejó de existir) conduce el proceso de una iniciativa de modelado: guarda el estado, asigna una skill a cada etapa y no deja cerrar una etapa sin una decisión del Data Scientist. Su núcleo no trae reglas metodológicas: cada proyecto las carga en un catálogo de golden rules. Este adaptador genera ese catálogo desde el toolkit, para que ai-mllc haga cumplir las prácticas y los chequeos de `domains/` sin reescribirlos.

| Capa | Quién la pone |
|---|---|
| Proceso, estado, etapas, cierre por decisión humana | ai-mllc |
| Qué es una buena práctica, con qué fuerza aplica y cómo se verifica | Este toolkit, a través del catálogo |
| Contexto y restricciones del proyecto | La constitución local del proyecto |

## Uso en un proyecto, de punta a punta

Una sola vez por proyecto, desde su raíz (ejemplo de crédito; para cobranzas, sumar `collections` al compose y usar `collections-ml`):

```bash
source ~/projects/ai-mllc/.venv/bin/activate
bash ~/projects/ai-mllc/adapters/claude/bootstrap.sh
python3 ~/projects/margara-toolkit/adapters/mllc/compose.py ml-foundations credit-scoring --out .claude/mllc-golden-rules.md --force
ln -s ~/.agents/skills/credit-scoring-ml .claude/skills/credit-scoring-ml
```

1. Completar `.claude/rules/mllc-constitution-local.md`: contexto, variables sensibles prohibidas, fuentes excluidas y acceso a datos.
2. Crear `forbidden_columns.txt` en la raíz combinando `ml-foundations/checks/forbidden_columns.example.txt` con la lista del dominio.
3. Sumar `credit-scoring-ml` a `support` de las etapas donde ayuda, con `/mllc-config` o con `mllc-core config set-binding`.
4. Trabajar con `/mllc` y las etapas. Al cerrar cada etapa, el agente evalúa las reglas de esa etapa: corre el chequeo, presenta la evidencia o lo discute, y registra el resultado. Una regla bloqueante en `no_cumple` o `evidencia_insuficiente` deja la etapa abierta hasta que se resuelva.

Para ajustar una regla a un proyecto, editarla en `.claude/mllc-golden-rules.md` (por ejemplo `estado: draft` para que no bloquee). Volver a componer pisa esas ediciones.

## Generar el catálogo

```bash
python3 ~/projects/margara-toolkit/adapters/mllc/compose.py ml-foundations --out .claude/mllc-golden-rules.md
```

Para un proyecto de crédito o de cobranzas, componer los dominios en orden (cada uno se apoya en los anteriores):

```bash
python3 ~/projects/margara-toolkit/adapters/mllc/compose.py ml-foundations credit-scoring --out .claude/mllc-golden-rules.md
python3 ~/projects/margara-toolkit/adapters/mllc/compose.py ml-foundations credit-scoring collections --out .claude/mllc-golden-rules.md
```

- La carpeta es la de configuración de ai-mllc en el proyecto: `.claude/` en Claude Code (`.cursor/`, `.kiro/` o `.github/` en las otras herramientas).
- Si el bootstrap de ai-mllc ya sembró un catálogo de referencia, reemplazarlo con `--force`. Sus tres reglas de referencia ya están incluidas en el catálogo del toolkit.
- `--check` valida todos los catálogos sin escribir nada. El formato que valida es el mismo que exige el núcleo de ai-mllc.
- Hay catálogo para `ml-foundations` (31 reglas, prefijo `ml-`), `credit-scoring` (20, `cr-`) y `collections` (13, `co-`). Los de dominio solo suman lo propio: no repiten las reglas generales.
- En cobranzas, las reglas de crédito pensadas para originación (por ejemplo `cr-sesgo-de-seleccion`, `cr-punto-de-corte`) se evalúan como `no_aplica` cuando no corresponden.
- `tests/test_mllc_catalogs.py` verifica el formato y que cada comando que nombra una regla use un chequeo y flags que existen.

## Cómo se evalúa cada regla

Cada regla declara fuerza, etapa, mecanismo y estado (ver `shared/knowledge/agent-workflow.md`, "Reglas con fuerza, mecanismo y estado").

- **`check_determinista`:** el enunciado dice qué script de `domains/ml-foundations/checks/` correr. Código de salida 0 → `cumple`; 1 → `no_cumple`; no se pudo correr por falta de insumos → `evidencia_insuficiente`.
- **`atestacion`:** el agente presenta la evidencia que pide el enunciado.
- **`discusion`:** se conversa con el Data Scientist y se registra lo acordado.

El resultado se registra con el comando de ai-mllc:

```bash
mllc-core evaluate-golden-rule --config-dir .claude --result-id <id> \
  --rule-id ml-integridad-del-dataset --rule-version 1 \
  --mechanism check_determinista --outcome no_cumple --expected-last-seq <seq>
```

Una regla `active` y bloqueante con `no_cumple` o `evidencia_insuficiente` mantiene la etapa abierta hasta que el Data Scientist la resuelva. Para probar una regla sin que bloquee, ponerla en `estado: draft` en el catálogo del proyecto.

## Mapeo de etapas

| Etapa de ai-mllc | Archivos del toolkit |
|---|---|
| `/mllc-discovery` (opcional, antes del intake; no es una etapa) | `templates/discovery.md`: la skill `discover-initiative` la usa si el proyecto tiene el toolkit, y deja `DISCOVERY_LOG.md` y un borrador del PRD |
| `intake` | `00-flujo.md` (¿hace falta ML?, problem framing, uso y respaldo) |
| `understand` | `08-trazabilidad.md`, `02-leakage.md` (observación vs. afirmación) |
| `observe` | `01-universo-particiones.md` |
| `features` | `02-leakage.md`, `03-features.md` |
| `dataset` | `03b-dataset.md` |
| `model` | `04-modelado.md`, `05-poblacion-y-sesgo.md` |
| `deploy` | `06-monitoreo.md`, `07-experimentacion.md`, `09-documentacion.md` |

## Skills del toolkit como soporte

Las skills de ai-mllc ejecutan cada etapa; las del toolkit aportan el criterio. Para que una etapa pueda consultarlas:

1. Enlazar la skill en la carpeta de skills del harness del proyecto, por ejemplo:
   `ln -s ~/.agents/skills/ml-practices .claude/skills/ml-practices`
   Aunque la skill ya esté instalada globalmente, `mllc-core` solo acepta en un binding skills que estén en la carpeta del proyecto.
2. Agregarla a `support` en los bindings de la etapa (`.claude/mllc-bindings.json`), sin cambiar la skill nuclear:

```json
{
  "bindings": {
    "model": {
      "capabilities": ["run-experiments", "evaluate-solution"],
      "nuclear": "ml-modeling-lab",
      "support": ["feature-selection", "notebook-report", "ml-practices"]
    }
  }
}
```

El ejemplo copia el binding de referencia de ai-mllc para `model` y solo suma `ml-practices` a `support`. Para otra etapa, hacer lo mismo con su binding de referencia.

## Constitución local

Las restricciones transversales del proyecto van en la constitución local de ai-mllc, no en el catálogo. Por ejemplo, para un proyecto de crédito: variables sensibles prohibidas y la lista de columnas prohibidas (`forbidden_columns.txt`) que usa `ml-sin-columnas-prohibidas`.

## Límites

- ai-mllc tiene adaptadores para Claude Code, Cursor, Kiro y Copilot. El de Claude Code se instala con `bash ~/projects/ai-mllc/adapters/claude/bootstrap.sh` desde la raíz del proyecto (ver `adapters/claude/README.md` en ai-mllc).
- ai-mllc termina en modelado, con despliegue opcional. Monitoreo continuo, impacto y reentrenamiento siguen en el toolkit (`06`, `07`).
- Las skills nucleares de ai-mllc traen parte de esta metodología escrita adentro. Si se contradicen con el toolkit, el criterio general vive acá; conviene que esas skills remitan al toolkit en lugar de repetirlo.
