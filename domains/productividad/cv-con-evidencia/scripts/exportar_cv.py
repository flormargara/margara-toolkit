#!/usr/bin/env python3
"""Exporta el subconjunto Markdown de formato_cv.md. Las salidas deben ser nuevas."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import tempfile


INLINE = re.compile(r'(\*\*[^*]+\*\*|\*[^*]+\*|\[[^\]]+\]\([^\s)]+\))')


def segmentos(texto):
    for part in INLINE.split(texto):
        if not part:
            continue
        if part.startswith('**') and part.endswith('**'):
            yield part[2:-2], True, False, None
        elif part.startswith('*') and part.endswith('*'):
            yield part[1:-1], False, True, None
        elif (m := re.fullmatch(r'\[([^\]]+)\]\(([^\s)]+)\)', part)):
            if not re.match(r'^(?:https?://|mailto:)', m[2], re.I):
                raise ValueError('Los enlaces deben usar https, http o mailto.')
            yield m[1], False, False, m[2]
        else:
            if any(c in part for c in ('*', '`', '<', '>')):
                raise ValueError('Formato inline no admitido; consultar formato_cv.md.')
            yield part, False, False, None


def parsear(texto):
    bloques = []
    for line in texto.splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith(('```', '~~~', '|', '>', '!', '<')) or re.match(r'^\d+[.)]\s', line):
            raise ValueError('Markdown no admitido: tablas, código, imágenes, HTML o listas numeradas.')
        kind, body = 'parrafo', line
        for marker, value in [('### ', 'rol'), ('## ', 'seccion'), ('# ', 'nombre'), ('- ', 'bullet')]:
            if line.startswith(marker):
                kind, body = value, line[len(marker):]
                break
        if body.startswith('#') or not body.strip():
            raise ValueError('Heading vacío o nivel no admitido.')
        if kind == 'parrafo' and '|' in body and any(k == 'seccion' for k, _ in bloques):
            if body.count('|') != 1:
                raise ValueError('Metadatos de rol requieren una sola separación institución | fechas.')
        list(segmentos(body))
        bloques.append((kind, body))
    if not bloques or bloques[0][0] != 'nombre' or sum(k == 'nombre' for k, _ in bloques) != 1:
        raise ValueError('La fuente debe empezar con un único # Nombre.')
    return bloques


def texto_plano(bloques):
    return '\n'.join(('- ' if kind == 'bullet' else '') + ''.join(s[0] for s in segmentos(body))
                     for kind, body in bloques) + '\n'


def escribir_docx(bloques, ruta, fuente):
    try:
        from docx import Document
        from docx.shared import Mm, Pt, RGBColor
        from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_TAB_ALIGNMENT
        from docx.oxml import OxmlElement
        from docx.oxml.ns import qn
        from docx.opc.constants import RELATIONSHIP_TYPE as RT
    except ImportError as exc:
        raise RuntimeError('Falta python-docx. Usá un runtime documental o instalalo en un entorno virtual.') from exc

    document = Document()
    document.core_properties.author = ''
    document.core_properties.last_modified_by = ''
    sec = document.sections[0]
    sec.page_width, sec.page_height = Mm(210), Mm(297)
    sec.top_margin = sec.bottom_margin = sec.left_margin = sec.right_margin = Mm(11)
    style = document.styles['Normal']
    style.font.name, style.font.size = fuente, Pt(10.5)
    style.font.color.rgb = RGBColor.from_string('282828')
    style.paragraph_format.space_after = Pt(3)
    style.paragraph_format.line_spacing = 1.03
    # Native list with a fixed tab after the marker and a hanging indent.
    numbering = document.part.numbering_part.element
    abs_ids = [int(e.get(qn('w:abstractNumId'))) for e in numbering.findall(qn('w:abstractNum'))]
    num_ids = [int(e.get(qn('w:numId'))) for e in numbering.findall(qn('w:num'))]
    abs_id, num_id = max(abs_ids, default=0) + 1, max(num_ids, default=0) + 1
    abstract = OxmlElement('w:abstractNum'); abstract.set(qn('w:abstractNumId'), str(abs_id))
    lvl = OxmlElement('w:lvl'); lvl.set(qn('w:ilvl'), '0')
    for tag, val in [('start', '1'), ('numFmt', 'bullet'), ('lvlText', '•'), ('suff', 'tab')]:
        node = OxmlElement('w:' + tag); node.set(qn('w:val'), val); lvl.append(node)
    abstract.append(lvl); numbering.append(abstract)
    num = OxmlElement('w:num'); num.set(qn('w:numId'), str(num_id))
    aid = OxmlElement('w:abstractNumId'); aid.set(qn('w:val'), str(abs_id)); num.append(aid); numbering.append(num)

    def inline(paragraph, text, bold=False, size=10.5):
        for visible, b, i, url in segmentos(text):
            run = paragraph.add_run(visible)
            run.bold, run.italic = bold or b, i
            run.font.name, run.font.size = fuente, Pt(size)
            run.font.color.rgb = RGBColor.from_string('000000' if run.bold else '282828')
            fonts = run._element.get_or_add_rPr().rFonts
            fonts.set(qn('w:ascii'), fuente); fonts.set(qn('w:hAnsi'), fuente)
            if url:
                link = OxmlElement('w:hyperlink')
                link.set(qn('r:id'), paragraph.part.relate_to(url, RT.HYPERLINK, is_external=True))
                paragraph._p.remove(run._r); link.append(run._r); paragraph._p.append(link)

    in_header = True
    for index, (kind, body) in enumerate(bloques):
        p = document.add_paragraph()
        fmt = p.paragraph_format
        if kind == 'seccion':
            in_header = False
            fmt.space_before, fmt.space_after, fmt.keep_with_next = Pt(7), Pt(3), True
            borders = OxmlElement('w:pBdr'); border = OxmlElement('w:bottom')
            for key, val in [('val', 'single'), ('sz', '4'), ('color', 'B0B0B0'), ('space', '2')]:
                border.set(qn('w:' + key), val)
            borders.append(border); p._p.get_or_add_pPr().append(borders)
            inline(p, body, bold=True, size=11)
        elif kind == 'nombre':
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            fmt.keep_with_next = True
            inline(p, body, bold=True, size=16)
        elif kind == 'rol':
            fmt.keep_with_next, fmt.space_before, fmt.space_after = True, Pt(4), Pt(1)
            inline(p, body, bold=True)
        elif kind == 'bullet':
            p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            fmt.left_indent, fmt.first_line_indent = Mm(4), Mm(-4)
            fmt.tab_stops.add_tab_stop(Mm(4))
            props = p._p.get_or_add_pPr(); np = OxmlElement('w:numPr')
            for tag, value in [('ilvl', '0'), ('numId', str(num_id))]:
                node = OxmlElement('w:' + tag); node.set(qn('w:val'), value); np.append(node)
            props.append(np)
            inline(p, body)
        elif in_header:
            p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY if body.startswith('*') else WD_ALIGN_PARAGRAPH.CENTER
            inline(p, body)
        elif '|' in body:
            left, right = body.split('|', 1)
            fmt.tab_stops.add_tab_stop(sec.page_width - sec.left_margin - sec.right_margin,
                                       WD_TAB_ALIGNMENT.RIGHT)
            fmt.keep_with_next = index + 1 < len(bloques) and bloques[index + 1][0] == 'bullet'
            inline(p, left.strip() + '\t' + right.strip())
        else:
            p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            inline(p, body)
    document.save(ruta)


def normalizar_paridad(texto):
    texto = re.sub(r'^\s*[-•]\s+', '', texto, flags=re.M)
    return ''.join(texto.split()).replace('|', '').replace('•', '').replace('\u00ad', '')


def convertir_pdf(docx, paginas, esperado):
    office = shutil.which('soffice') or shutil.which('libreoffice')
    if not office or not shutil.which('pdftotext'):
        raise RuntimeError('PDF requiere LibreOffice y pdftotext de Poppler.')
    pdf = docx.with_suffix('.pdf')
    with tempfile.TemporaryDirectory(prefix='cv-office-') as temp:
        subprocess.run([office, f'-env:UserInstallation={Path(temp).as_uri()}', '--headless',
                        '--convert-to', 'pdf', '--outdir', str(docx.parent), str(docx)],
                       check=True, capture_output=True, text=True, timeout=120)
    if not pdf.is_file() or not pdf.stat().st_size:
        raise RuntimeError('La conversión no produjo PDF; TXT y DOCX quedan disponibles.')
    result = subprocess.run(['pdftotext', '-layout', str(pdf), '-'], check=True, capture_output=True,
                            text=True, timeout=60)
    count = result.stdout.count('\f')
    if count != paginas:
        raise RuntimeError(f'PDF de {count} páginas; se esperaban {paginas}. Revisar selección y formato.')
    if normalizar_paridad(result.stdout) != normalizar_paridad(esperado):
        raise RuntimeError('La extracción del PDF difiere de la fuente. Revisar paridad antes de entregar.')
    return {'paginas': count, 'paridad_pdf': True, 'texto_seleccionable': bool(result.stdout.strip())}


def exportar(fuente, salida, pdf=False, solo_texto=False, paginas=1, tipografia='Noto Serif'):
    bloques = parsear(fuente.read_text(encoding='utf-8'))
    texto = texto_plano(bloques)
    if salida.exists() and any(salida.iterdir()):
        raise ValueError('La salida debe ser una carpeta nueva o vacía; no se sobrescriben entregables.')
    salida.mkdir(parents=True, exist_ok=True)
    txt = salida / 'cv.txt'; txt.write_text(texto, encoding='utf-8')
    controles = {'txt_desde_fuente': True}
    archivos = [txt]
    if not solo_texto:
        docx = salida / 'cv.docx'
        escribir_docx(bloques, docx, tipografia)
        archivos.append(docx)
        if pdf:
            controles.update(convertir_pdf(docx, paginas, texto))
            archivos.append(salida / 'cv.pdf')
    reporte = {'fuente_sha256': hashlib.sha256(fuente.read_bytes()).hexdigest(),
               'archivos': {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in archivos},
               'controles': controles, 'revision_visual': 'pendiente', 'auditoria_factual': 'pendiente'}
    (salida / 'exportacion.json').write_text(json.dumps(reporte, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    return reporte


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--fuente', required=True, type=Path)
    parser.add_argument('--salida', required=True, type=Path)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--pdf', action='store_true')
    mode.add_argument('--solo-texto', action='store_true')
    parser.add_argument('--paginas', type=int, default=1)
    parser.add_argument('--fuente-tipografica', default='Noto Serif')
    args = parser.parse_args()
    if args.paginas < 1:
        parser.error('--paginas debe ser positivo.')
    try:
        reporte = exportar(args.fuente.resolve(), args.salida.resolve(), args.pdf,
                           args.solo_texto, args.paginas, args.fuente_tipografica)
        print(json.dumps(reporte, indent=2, ensure_ascii=False))
    except (OSError, ValueError, RuntimeError, subprocess.SubprocessError) as exc:
        parser.exit(1, f'EXPORTACIÓN INCOMPLETA: {exc}\n')


if __name__ == '__main__':
    main()
