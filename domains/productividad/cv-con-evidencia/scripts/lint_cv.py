#!/usr/bin/env python3
"""Controles parciales. No demuestra autoría, trazabilidad ni calidad editorial."""
import argparse
from pathlib import Path
import re
import shutil
import subprocess
import unicodedata
import xml.etree.ElementTree as ET

KB_FILES = ('kb_decisiones_canonicas.md', 'kb_experiencias.md',
            'kb_capacidades.md', 'kb_preferencias_cv.md')


def normalizar(texto):
    return ''.join(c for c in unicodedata.normalize('NFKD', texto.casefold())
                   if not unicodedata.combining(c))


def revisar(texto, kb, max_palabras=620):
    errores, avisos = [], []
    if not texto.strip():
        errores.append('El CV está vacío.')
    if len(texto.split()) > max_palabras:
        avisos.append(f'Se superó el presupuesto orientativo de {max_palabras} palabras; revisar selección.')
    for nombre in KB_FILES:
        if not (kb / nombre).is_file():
            errores.append(f'Falta la fuente activa {nombre}.')
    canon = kb / KB_FILES[0]
    if canon.exists() and 'Todavía no hay hechos confirmados.' in canon.read_text(encoding='utf-8'):
        errores.append('La plantilla canónica todavía no tiene hechos confirmados.')
    corpus = ' '.join((kb / n).read_text(encoding='utf-8') for n in KB_FILES if (kb / n).is_file())
    anios = set(re.findall(r'\b(?:19|20)\d{2}\b', corpus))
    for anio in sorted(set(re.findall(r'\b(?:19|20)\d{2}\b', texto)) - anios):
        avisos.append(f'Año {anio} ausente de KB: comprobar la fecha y su fuente exacta.')
    nums = set(re.findall(r'\d+(?:[.,]\d+)*', corpus))
    for linea in texto.splitlines():
        if not re.match(r'^\s*[-•]\s+', linea):
            continue
        for numero in re.findall(r'\d+(?:[.,]\d+)*', linea):
            if numero not in nums:
                avisos.append(f'Número {numero} ausente de KB en bullet: comprobar respaldo y contexto.')
        inicio = re.sub(r'^\s*[-•]\s+', '', linea).split(maxsplit=1)
        if inicio and (normalizar(inicio[0]) in ('yo', 'i', 'he', 'she', 'el', 'ella')
                       or re.fullmatch(r'[A-Za-zÁÉÍÓÚáéíóúÑñ]+ó', inicio[0])):
            avisos.append(f'Revisar primera persona implícita: {linea.strip()}')
    for frase in ('results-driven', 'world-class', 'highly motivated', 'de vanguardia', 'de manera integral'):
        if frase in normalizar(texto):
            avisos.append(f'Revisar voz genérica: {frase}.')
    if '—' in texto or '―' in texto:
        avisos.append('Revisar guion largo según la referencia de voz.')
    return errores, list(dict.fromkeys(avisos))


def revisar_pdf(ruta, paginas):
    if not shutil.which('pdftotext'):
        raise RuntimeError('Falta pdftotext de Poppler para comprobar el PDF.')
    result = subprocess.run(['pdftotext', '-bbox', str(ruta), '-'], check=True,
                            capture_output=True, text=True, timeout=60)
    tree = ET.fromstring(result.stdout)
    pages = [n for n in tree.iter() if n.tag.endswith('page')]
    errores, avisos = [], []
    if len(pages) != paginas:
        errores.append(f'PDF de {len(pages)} páginas; se esperaban {paginas}.')
    for i, page in enumerate(pages, 1):
        words = [n for n in page.iter() if n.tag.endswith('word')]
        if not words:
            errores.append(f'Página {i} sin texto extraíble.')
        elif max(float(n.attrib['yMax']) for n in words) / float(page.attrib['height']) < .80:
            avisos.append(f'Página {i} con espacio amplio: revisar omisiones y justificar selección; no bloquea por sí solo.')
    return errores, avisos


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cv', required=True, type=Path)
    parser.add_argument('--kb', required=True, type=Path)
    parser.add_argument('--pdf', type=Path)
    parser.add_argument('--paginas', type=int, default=1)
    parser.add_argument('--max-palabras', type=int, default=620)
    args = parser.parse_args()
    if args.paginas < 1 or args.max_palabras < 1:
        parser.error('Páginas y presupuesto deben ser positivos.')
    try:
        errores, avisos = revisar(args.cv.read_text(encoding='utf-8'), args.kb, args.max_palabras)
        if args.pdf:
            ep, ap = revisar_pdf(args.pdf, args.paginas)
            errores.extend(ep)
            avisos.extend(ap)
    except (OSError, ValueError, RuntimeError, subprocess.SubprocessError, ET.ParseError) as exc:
        parser.exit(2, f'CONTROL NO COMPLETADO: {exc}\n')
    for e in errores:
        print(f'ERROR: {e}')
    for a in avisos:
        print(f'AVISO: {a}')
    print('Seniority, fechas, métricas y cada afirmación se contrastan manualmente con su fuente.')
    print('RESULTADO: ' + ('BLOQUEADO' if errores else 'PASA controles mecánicos parciales'))
    return 1 if errores else 0


if __name__ == '__main__':
    raise SystemExit(main())
