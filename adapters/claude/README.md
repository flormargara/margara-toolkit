# Adaptador para Claude Code

| Pieza | Dónde va | Cómo |
|---|---|---|
| `skills/credit-scoring-ml/` | `~/.agents/skills/` y `~/.claude/skills/` (global) | `./scripts/install.sh` |
| `skills/collections-ml/` | Igual | `./scripts/install.sh` |
| `skills/cv-con-evidencia/` | Igual | `./scripts/install.sh` |
| `rules/credit-scoring-guardrails.md` | `.claude/rules/` del proyecto | Copiar al proyecto |
| `settings.example.json` | `.claude/settings.json` del proyecto | Copiar el bloque `hooks` y ajustar los `--include` |

## Las skills

Cada carpeta de `skills/` contiene solo su `SKILL.md`. El resto son enlaces simbólicos a `domains/` y `shared/`, así el contenido existe una sola vez:

| Skill | Enlaces |
|---|---|
| `credit-scoring-ml` | `references/` → conocimiento de credit-scoring; `templates/`; `scripts/` → chequeos; `shared/` → flujo de trabajo con agentes |
| `collections-ml` | `references/` → conocimiento de cobranzas; `templates/`; `credit-scoring/` → conocimiento de credit-scoring; `scripts/` → chequeos |
| `cv-con-evidencia` | La carpeta completa de `domains/productividad/cv-con-evidencia` |

## El hook de leakage

Después de cada edición de código, escanea el archivo editado en busca de columnas prohibidas. Si encuentra alguna, sale con código 2 y Claude recibe el mensaje para corregir o justificar.

- **`--include`:** limita el escaneo a las carpetas de features y modelado. Ajustar a la estructura real de cada proyecto. Sin `--include` escanea todo `.py`, `.sql` e `.ipynb`.
- **Patrones:** usa `forbidden_columns.txt` de la raíz del proyecto. Crearlo copiando `domains/credit-scoring/checks/forbidden_columns.example.txt` y adaptándolo a los nombres reales de columnas.
- **Usos legítimos:** el código que construye el target sí usa columnas de mora. Marcar esas líneas con el comentario `leakage-ok`, o dejar esa carpeta fuera de `--include`.

## Pendiente

- Hook que bloquee el entrenamiento si `check_universe.py` no pasó: depende de cómo se lance el entrenamiento en cada proyecto.
- Hook de cierre que exija la ficha del modelo actualizada.
- `check_traceability.py`: porcentaje de registros que sobreviven cada join de la cadena evaluación → desempeño. Depende de las tablas de cada organización.
- Subagente revisor de modelos: se agrega si el uso muestra que hace falta.
