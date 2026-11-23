# Adaptador para Claude Code

| Pieza | Dónde va | Cómo |
|---|---|---|
| `skills/ml-practices/` | `~/.agents/skills/` y `~/.claude/skills/` (global) | `./scripts/install.sh` |
| `skills/credit-scoring-ml/` | Igual | `./scripts/install.sh` |
| `skills/collections-ml/` | Igual | `./scripts/install.sh` |
| `skills/cv-con-evidencia/` | Igual | `./scripts/install.sh` |
| `rules/ml-guardrails.md` | `.claude/rules/` de cualquier proyecto de ML | Copiar al proyecto |
| `rules/credit-scoring-guardrails.md` | `.claude/rules/` de un proyecto de crédito, junto con la anterior | Copiar al proyecto |
| `settings.example.json` | `.claude/settings.json` del proyecto | Copiar el bloque `hooks` y ajustar los `--include` |

## Las skills

Cada carpeta de `skills/` contiene solo su `SKILL.md`. El resto son enlaces simbólicos a `domains/` y `shared/`, así el contenido existe una sola vez. Los enlaces a dominios completos mantienen la misma ruta que usan los archivos de conocimiento para citarse entre sí (por ejemplo, `ml-foundations/knowledge/01-universo-particiones.md`).

| Skill | Enlaces |
|---|---|
| `ml-practices` | `ml-foundations/` → dominio genérico de ML; `shared/` → flujo de trabajo con agentes |
| `credit-scoring-ml` | `references/` → conocimiento de crédito; `templates/`; `patterns/` → lista de leakage de crédito; `ml-foundations/`; `shared/` |
| `collections-ml` | `references/` → conocimiento de cobranzas; `templates/`; `credit-scoring/` → dominio de crédito; `ml-foundations/` |
| `cv-con-evidencia` | La carpeta completa de `domains/productividad/cv-con-evidencia` |

## El hook de leakage

Después de cada edición de código, escanea el archivo editado en busca de columnas prohibidas. Si encuentra alguna, sale con código 2 y Claude recibe el mensaje para corregir o justificar.

- **`--include`:** limita el escaneo a las carpetas de features y modelado. Ajustar a la estructura real de cada proyecto. Sin `--include` escanea todo `.py`, `.sql` e `.ipynb`.
- **Patrones:** usa `forbidden_columns.txt` de la raíz del proyecto. Crearlo combinando `domains/ml-foundations/checks/forbidden_columns.example.txt` con la lista del dominio (por ejemplo `domains/credit-scoring/checks/forbidden_columns.example.txt`) y adaptándolo a los nombres reales de columnas. Si no existe, usa la lista genérica.
- **Usos legítimos:** el código que construye el target sí usa columnas de resultado. Marcar esas líneas con el comentario `leakage-ok`, o dejar esa carpeta fuera de `--include`.

## Pendiente

- Hook que bloquee el entrenamiento si `check_universe.py` no pasó: depende de cómo se lance el entrenamiento en cada proyecto.
- Hook de cierre que exija la ficha del modelo actualizada.
- `check_traceability.py`: porcentaje de registros que sobreviven cada join de la cadena predicción → resultado. Depende de las tablas de cada organización.
- Subagente revisor de modelos: se agrega si el uso muestra que hace falta.
