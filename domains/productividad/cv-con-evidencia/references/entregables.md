# Generar y verificar archivos

Conservá el texto aprobado. Usá el formato de fuente de `formato_cv.md`. El generador incluido procesa CVs en ese subconjunto de Markdown; otras estructuras y cartas necesitan una herramienta apropiada disponible y los mismos controles.

## Comprobar y generar

1. Ejecutá `python3 <skill>/scripts/comprobar_entorno.py`. Si falta una dependencia, informá la capacidad afectada. Una ejecución parcial no aprueba formatos inexistentes.
2. Conservá los entregables reemplazados en `versiones/`. Ejecutá `python3 <skill>/scripts/exportar_cv.py --fuente <aplicacion>/cv.md --salida <directorio-nuevo> --pdf`. Para otra extensión usá `--paginas N`; la preferencia se registra en estrategia. `--fuente-tipografica` permite usar otra fuente instalada.
3. El script genera TXT y DOCX; con `--pdf` convierte ese DOCX usando LibreOffice con perfil temporal aislado. Rechaza sobrescribir salidas; elegí una carpeta nueva por ejecución y promovela después de verificarla. Si falla el PDF, conserva TXT/DOCX e informa el fallo. El proceso de conversión tiene tiempo límite.
4. Comprobá que TXT y DOCX contienen el mismo texto que la fuente, y que el texto extraído del PDF coincide salvo viñetas y espacio. El script comprueba esta última paridad, páginas y texto seleccionable cuando se pide PDF. Un control fallido devuelve error, aunque deje archivos para diagnóstico.
5. Ejecutá `python3 <skill>/scripts/lint_cv.py --cv <cv.txt> --kb <espacio>/kb --pdf <cv.pdf> --paginas N`. Podés ajustar `--max-palabras`; el presupuesto orienta la revisión y el PDF decide la extensión real.

Para generar solo TXT, usá `--solo-texto`, sin instalar librerías documentales. Guardá siempre el mismo contenido semántico en todos los formatos.

## Inspección visual y cierre

Renderizá cada página con `pdftoppm -png -r 120 <cv.pdf> <prefijo>` o el renderer documental del entorno. Abrí todas las imágenes. Comprobá cortes, superposición, caracteres, jerarquía, alineación de fechas, sangría de bullets y legibilidad. La extracción de texto no demuestra calidad visual.

Si el contenido desborda, volvé a estrategia y redacción. Si solo falla el layout, corregí formato y repetí exportación, paridad y render. Si cambia el texto, actualizá revisión independiente y auditoría de lo afectado.

El generador emite `exportacion.json` con hash de fuente, hashes de salidas y controles mecánicos ejecutados. No declara revisión visual ni factual. Registrá en `auditoria.md` la inspección visual real y el estado final; actualizá la ficha de aplicación. Entregá Markdown, TXT, Word y PDF vigentes junto con una lista breve de decisiones y pendientes.
