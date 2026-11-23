# Adaptador para Claude Code

| Pieza | Dónde va | Cómo |
|---|---|---|
| `skills/credit-scoring-ml/` | `~/.claude/skills/` (global) | `./scripts/install-claude.sh` crea el enlace simbólico |
| `rules/credit-scoring-guardrails.md` | `.claude/rules/` del proyecto | Copiar al proyecto |
| `settings.example.json` | `.claude/settings.json` del proyecto | Copiar el bloque `hooks` y ajustar los `--include` |

## La skill

`skills/credit-scoring-ml/` contiene solo `SKILL.md`. Sus carpetas `references/`, `templates/` y `scripts/` son enlaces simbólicos a `domains/credit-scoring/`, así el contenido existe una sola vez.

## El hook de leakage

Después de cada edición de código, escanea el archivo editado en busca de columnas prohibidas. Si encuentra alguna, sale con código 2 y Claude recibe el mensaje para corregir o justificar.

- **`--include`:** limita el escaneo a las carpetas de features y modelado. Ajustar a la estructura real de cada proyecto. Sin `--include` escanea todo `.py`, `.sql` e `.ipynb`.
- **Patrones:** usa `forbidden_columns.txt` de la raíz del proyecto. Crearlo copiando `domains/credit-scoring/checks/forbidden_columns.example.txt` y adaptándolo a los nombres reales de columnas.
- **Usos legítimos:** el código que construye el target sí usa columnas de mora. Marcar esas líneas con el comentario `leakage-ok`, o dejar esa carpeta fuera de `--include`.

## Pendiente

- Hook que bloquee el entrenamiento si no hay configuración de split temporal: depende de cómo se lance el entrenamiento en cada proyecto.
- Hook de cierre que exija la ficha del modelo actualizada.
- Subagente revisor de modelos: se agrega si el uso muestra que hace falta.
