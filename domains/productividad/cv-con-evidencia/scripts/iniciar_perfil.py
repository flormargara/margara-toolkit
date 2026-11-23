#!/usr/bin/env python3
"""Crea un espacio personal nuevo; nunca sobrescribe uno existente."""
import argparse
from pathlib import Path
import shutil


def iniciar(destino):
    raiz = Path(__file__).resolve().parents[1]
    destino = Path(destino).expanduser().resolve()
    if destino == raiz or raiz in destino.parents:
        raise ValueError('El espacio personal debe estar fuera de la instalación del skill.')
    if destino.exists():
        raise ValueError('El destino ya existe. Elegí una carpeta nueva para conservar sus archivos.')
    destino.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(raiz / 'assets' / 'workspace', destino)
    return destino


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--destino', required=True)
    args = parser.parse_args()
    try:
        print(f'Espacio creado: {iniciar(args.destino)}')
        print('Las plantillas están vacías. Continuá con references/armar_kb.md del skill.')
    except (ValueError, OSError) as exc:
        parser.exit(1, f'ERROR: {exc}\n')


if __name__ == '__main__':
    main()
