# Features — [proyecto] — [tema]

Tres partes en un mismo archivo: el backlog de ideas, el inventario de fuentes y el handoff de las features priorizadas (`knowledge/03-features.md`, "Ideación"). Todo nombre, columna, join, partición y rango temporal sale de una fuente verificada; lo que falta se marca como pendiente, no se completa con nombres plausibles.

| Campo | Valor |
|---|---|
| Decisión que apoya el modelo | |
| Entidad y grano | |
| Universo (archivo o consulta) | |
| Fecha de corte o período | |
| Fecha | |

## Backlog de ideas

Una fila por hipótesis y una por dominio sin idea aplicable. Las descartadas se conservan: pueden volverse factibles si cambian los datos.

| Hipótesis | Mecanismo de negocio | Dominio / fuente | Potencial (1-5) | Factibilidad (1-5) | Puntaje | Estado (priorizada / idea / descartada / sin fuente) |
|---|---|---|---|---|---|---|
| | | | | | | |

## Inventario de fuentes

Una sección por fuente confirmada, aunque no haya terminado en una feature priorizada.

### [fuente o tabla]

- Grano:
- Claves de join y su tipo:
- Partición y cadencia:
- Historial disponible:
- Columnas relevantes:
- Significado de los eventos y filtros (procedencia: confirmada / observada):
- Verificado con (consulta o documento) y fecha:

## Handoff

Solo las features priorizadas. Si una feature combina varias fuentes, repetir el bloque de fuente y describir la ruta de joins.

### `FUENTE_DOMINIO_OPERACION_DESCRIPCION_VENTANA`

- Mecanismo de negocio:
- Definición funcional (qué calcula, sin SQL inventado):
- Grano de salida:
- Fuente: tabla, grano de entrada, columnas
- Joins:
- Eventos y filtros válidos:
- Temporalidad (columna de tiempo, ventana y relación con la fecha de corte):
- Evidencia que respaldó la priorización:
- Supuestos y pendientes (o "ninguno conocido"):

## Construcción

Se completa al construir (`knowledge/03-features.md`, "Fabricabilidad").

| Feature | Estado (construida / reutilizada / no fabricable / handoff incompleto) | Razón | Faltantes | Duplicados de grano | SQL o código |
|---|---|---|---|---|---|
| | | | | | |
