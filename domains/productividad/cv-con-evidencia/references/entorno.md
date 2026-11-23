# Entorno de ejecución

## Rutas y capacidades

Resuelve scripts y referencias contra la carpeta que contiene `SKILL.md`. Resuelve KB y aplicaciones contra el espacio personal elegido. En comandos con espacios, citá cada argumento. No guardes datos personales en la instalación del skill ni instales dependencias globales automáticamente.

El armado de KB y las instrucciones no dependen de otro skill, servicio, credencial ni modelo específico. Los scripts requieren Python 3.10 o posterior. `iniciar_perfil.py` y el lint básico usan solo la biblioteca estándar. Para exportar a Word se necesita `python-docx`; PDF requiere LibreOffice y los controles requieren Poppler, con `pdftotext`, `pdfinfo` y `pdftoppm`. Ejecutá `python3 <skill>/scripts/comprobar_entorno.py` para ver capacidades disponibles. No reemplaza permisos del entorno.

En Codex, aprovechá el runtime documental disponible si existe. En otros entornos puede usarse un entorno virtual con `python -m pip install python-docx`. Si se necesita instalar software del sistema, explicá qué falta y usá el mecanismo autorizado del entorno. La falta de exportador no impide preparar KB y contenido, pero deja pendientes esos entregables.

Las fuentes web se consultan solo si son necesarias o pedidas. Los documentos locales y el relato de la persona permiten trabajar sin red. Para afirmaciones sobre empresas, productos o requisitos cambiantes, consultá fuentes primarias vigentes. No mezcles esa investigación con evidencia sobre experiencia personal.

## Revisión independiente en Codex

Cuando haya herramientas de subagentes, creá un revisor sin heredar la conversación, por ejemplo con `fork_turns="none"` si esa opción existe. Pasá únicamente el encargo de `revision_senior_cv.md`, criterio editorial, JD y CV en la primera lectura. Después compartí estrategia y pasajes de respaldo. Conservá el mismo revisor para verificar resoluciones cuando sea posible. La delegación se limita a esta revisión y a las pruebas del skill solicitadas.

## Revisión independiente en Claude Code

Usá la herramienta de agente disponible para un revisor separado y limitá su encargo inicial a esos mismos materiales. Comprobá si recibe conversación u otros antecedentes. Si la configuración no permite aislar la lectura, prepará el encargo para una sesión nueva, con rutas accesibles y sin el historial del redactor. No necesitás crear un agente persistente ni copiar configuraciones heredadas.

## Sin delegación

Guardá `encargo_revision.md` en la aplicación con objetivo, rutas de JD/CV y referencias editoriales. Indicá que la primera lectura precede a recibir estrategia y fuentes. La persona puede abrir una sesión nueva para ejecutarlo. La autolectura puede ayudar a corregir, pero la revisión independiente queda pendiente hasta recibir y resolver el diagnóstico.
