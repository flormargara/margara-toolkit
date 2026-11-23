# Trazabilidad

Sin poder reconstruir qué evaluación generó qué oferta, qué oferta terminó en qué desembolso y cómo pagó ese desembolso, no se puede hacer backtest, medir el modelo en producción ni entrenar la versión siguiente. La trazabilidad es un requisito previo del modelado, no una tarea de datos aparte.

## La cadena

```
solicitud / evaluación → consulta a burós → oferta → aceptación → desembolso → desempeño de pago
```

Cada salto necesita una **clave única y estable** que esté en ambos lados. Problemas típicos que rompen la cadena:

- La clave del lado destino no existe o tiene otro formato.
- Una tabla tiene menos registros que otra que debería contener los mismos (registros que se pierden en una sincronización).
- La clave cambia de significado en una fecha (por ejemplo, de identificador de persona a número de cuenta) y las consultas necesitan condiciones distintas por período.
- Columnas de identificación sin parsear dentro de un JSON.
- Deduplicaciones no deterministas (`row_number()` sobre una clave que no es única en una de las tablas), que hacen que la misma consulta devuelva resultados distintos.
- Fechas con formato incorrecto en tablas de origen.

## Qué registrar en cada evaluación

- Identificador de la evaluación, de la persona y del producto.
- Score, rating y **versión del modelo**.
- **Versión de la política o ID de campaña** que tomó la decisión.
- Resultado de cada regla y motivo de rechazo.
- Identificadores de las consultas a burós usadas.
- El score de todos los solicitantes, incluidos los rechazados por reglas (ver `06-sesgo-seleccion.md`).

## Medir la trazabilidad como un indicador

Para cada salto, calcular qué porcentaje de registros encuentra su par en la tabla siguiente, por mes y por producto. Publicarlo como indicador de calidad con un umbral, y tratar una caída como un incidente.

Ante un problema, documentar:

- Período y volumen afectado.
- Si la corrección es retroactiva o solo hacia adelante.
- Quién lo detecta, quién lo corrige y por qué canal se notifica.
- Qué modelos, tableros o análisis quedan invalidados mientras tanto.

## Consecuencia práctica para un proyecto de scoring

Antes de construir un universo, medir la cobertura de cada salto para el período candidato. Si una parte relevante de las evaluaciones no se puede unir con su desempeño, el universo usable puede ser mucho más chico que el aparente, y además sesgado (por ejemplo, solo ciertos canales quedan trazados). Documentarlo en la ficha del modelo como limitación.
