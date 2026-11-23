#!/usr/bin/env bash
# Enlaza las skills del toolkit en ~/.claude/skills/ (enlaces simbólicos, no copias).
# Seguro de correr varias veces. No pisa carpetas reales con el mismo nombre.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DEST="${CLAUDE_HOME:-$HOME/.claude}/skills"
mkdir -p "$DEST"

for skill in "$ROOT"/adapters/claude/skills/*/; do
  name="$(basename "$skill")"
  target="$DEST/$name"
  if [ -L "$target" ]; then
    ln -sfn "${skill%/}" "$target"
    echo "actualizado: $name"
  elif [ -e "$target" ]; then
    echo "omitido: $target ya existe y no es un enlace (revisalo a mano)" >&2
  else
    ln -s "${skill%/}" "$target"
    echo "instalado:  $name -> $target"
  fi
done
