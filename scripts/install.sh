#!/usr/bin/env bash
# Instala las skills del toolkit para todas las herramientas.
#
# 1. ~/.agents/skills/<skill>  -> enlace a adapters/claude/skills/<skill> de este repo
#    (ubicación común; algunas herramientas la leen directamente)
# 2. <carpeta de cada herramienta>/<skill> -> enlace a ~/.agents/skills/<skill>
#
# Solo gestiona las skills del catálogo (adapters/claude/skills/). Nunca pisa una
# carpeta o archivo real: si existe algo que no es un enlace, lo informa y sigue.
# Seguro de correr varias veces.
#
# Uso:
#   ./scripts/install.sh              instala o actualiza
#   ./scripts/install.sh --uninstall  quita solo los enlaces que apuntan a este repo
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CATALOG="$ROOT/adapters/claude/skills"
AGENTS_DIR="${AGENTS_SKILLS_DIR:-$HOME/.agents/skills}"

# Herramientas que necesitan su propia carpeta. Agregar una es agregar una línea.
TOOL_DIRS=(
  "${CLAUDE_HOME:-$HOME/.claude}/skills"
)

link() {  # link <destino> <enlace>
  local target="$1" path="$2"
  if [ -L "$path" ]; then
    ln -sfn "$target" "$path"
    echo "actualizado: $path"
  elif [ -e "$path" ]; then
    echo "omitido:     $path ya existe y no es un enlace (revisalo a mano)" >&2
  else
    ln -s "$target" "$path"
    echo "instalado:   $path"
  fi
}

unlink_if_ours() {  # borra el enlace solo si resuelve dentro de este repo
  local path="$1"
  if [ -L "$path" ]; then
    local resolved
    resolved="$(cd "$path" 2>/dev/null && pwd -P || true)"
    case "$resolved" in
      "$ROOT"/*) rm "$path"; echo "quitado:     $path" ;;
      *) echo "omitido:     $path apunta fuera de este repo" >&2 ;;
    esac
  fi
}

if [ "${1:-}" = "--uninstall" ]; then
  for skill in "$CATALOG"/*/; do
    name="$(basename "$skill")"
    for dir in "${TOOL_DIRS[@]}"; do unlink_if_ours "$dir/$name"; done
    unlink_if_ours "$AGENTS_DIR/$name"
  done
  exit 0
fi

mkdir -p "$AGENTS_DIR"
for dir in "${TOOL_DIRS[@]}"; do mkdir -p "$dir"; done

for skill in "$CATALOG"/*/; do
  name="$(basename "$skill")"
  link "${skill%/}" "$AGENTS_DIR/$name"
  for dir in "${TOOL_DIRS[@]}"; do
    link "$AGENTS_DIR/$name" "$dir/$name"
  done
done
