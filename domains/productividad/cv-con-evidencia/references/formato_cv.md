# Formato predeterminado

La estrategia registra las excepciones pedidas por la persona o el destinatario. Estos valores son del método, no preferencias personales confirmadas.

## Página y jerarquía

Una página A4 por defecto, una columna, sin tablas de layout, cuadros de texto ni texto en imágenes. Márgenes de 11 mm y cuerpo de al menos 10,5 pt. Usá Noto Serif si está disponible, Liberation Serif como alternativa, o una serif legible disponible registrada en la estrategia. Nombre de 16 pt y secciones de 11 pt. Texto negro o gris muy oscuro y contraste legible.

Si el contenido desborda, revisá selección y retirá el mensaje de menor valor desde la estrategia antes de reducir legibilidad. Si termina antes del último quinto, revisá evidencia fuerte omitida o poco desarrollada. Con omisiones justificadas, el blanco es aceptable. La ocupación es una señal editorial, no un bloqueo mecánico.

La jerarquía distingue identidad y posicionamiento, secciones y evidencia. Nombre, puestos, grado y categorías de capacidades pueden llevar negrita. Los títulos de sección llevan una línea fina gris como borde de párrafo. El énfasis dentro de bullets es opcional y destaca solo detalles con función probatoria. El texto debe funcionar también sin esos énfasis.

## Encabezado y cuerpo

Centrar nombre, posicionamiento opcional y contacto autorizado disponible. Usá ciudad y país si se conocen. Teléfono, enlaces profesionales, movilidad y ciudadanía entran por preferencia y pertinencia. GitHub no es requisito general. Foto solo por pedido confirmado; omití identificadores personales y dirección exacta.

El resumen, si aporta una relación nueva entre experiencias, va después del encabezado en cursiva y sin título propio. Cuerpo y bullets pueden justificarse; conservá alineación de títulos y fechas. Las viñetas son listas nativas con sangría francesa y tabulación fija. Inspeccioná primera línea y continuaciones.

Cada rol tiene título en su propia línea en negrita, institución y fechas debajo sin negrita. Markdown/TXT separan institución y fechas con `|`; Word/PDF usan tabulación derecha. Educación usa el mismo patrón para grado y universidad/fechas. Conservá una forma consistente por institución y fechas con igual precisión.

En inglés pueden usarse Experience, Education, Skills, Languages, Certifications y Volunteering. En español, Experiencia, Educación, Habilidades técnicas, Idiomas, Certificaciones y Voluntariado. La estrategia adapta secciones al perfil y al idioma. La docencia seleccionada puede compartir Experiencia con los demás roles. Un proyecto académico se presenta como tal, sin convertirlo en cargo contractual; una investigación laboral conserva su cargo real.

## Fuente para el generador incluido

`exportar_cv.py` admite este subconjunto de Markdown, con una línea por párrafo:

```markdown
# Nombre de la persona
Área profesional | Especialidad
Ciudad, país | correo@example.com

*Resumen opcional con hechos autorizados.*

## Experiencia
### Cargo real o variante autorizada
Institución | 2020-2024
- Contribución y evidencia autorizadas.

## Educación
### Título académico
Institución | 2015-2019

## Habilidades técnicas
**Categoría:** Capacidades confirmadas.
```

`#` identifica el nombre, `##` secciones y `###` puestos o grados. `**texto**` y `*texto*` indican negrita y cursiva. Enlaces usan `[texto](URL)`; se conserva el rótulo visible y el vínculo en Word/PDF. Los demás elementos Markdown, tablas, HTML e imágenes requieren otra herramienta y una nueva comprobación de paridad. El generador rechaza bloques de código y tablas; no interpreta Markdown completo.

DOCX y PDF provienen del mismo contenido y conservan texto seleccionable. `cv.txt` contiene las mismas palabras salvo marcas y viñetas de formato. La redacción y su revisión de voz se rigen por `criterio_editorial_cv.md` y `voz.md`.
