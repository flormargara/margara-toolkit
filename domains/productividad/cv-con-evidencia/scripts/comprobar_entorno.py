#!/usr/bin/env python3
"""Informa capacidades sin instalar ni modificar software."""
import importlib.util
import json
import shutil
import sys


def comprobar():
    return {
        'python_compatible': sys.version_info >= (3, 10),
        'python_docx': importlib.util.find_spec('docx') is not None,
        'libreoffice': shutil.which('soffice') or shutil.which('libreoffice'),
        'pdftotext': shutil.which('pdftotext'),
        'pdfinfo': shutil.which('pdfinfo'),
        'pdftoppm': shutil.which('pdftoppm'),
    }


if __name__ == '__main__':
    print(json.dumps(comprobar(), indent=2, ensure_ascii=False))
