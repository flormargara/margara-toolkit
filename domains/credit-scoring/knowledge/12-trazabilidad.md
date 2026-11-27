# Trazabilidad en crédito

Aplica todo `ml-foundations/knowledge/08-trazabilidad.md`: claves únicas en cada salto, qué registrar en cada predicción y la trazabilidad medida como indicador. Acá está la cadena concreta de crédito.

Sin poder reconstruir qué evaluación generó qué oferta, qué oferta terminó en qué desembolso y cómo pagó ese desembolso, no se puede hacer backtest, medir el score en producción ni entrenar la versión siguiente.

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

## Consecuencia práctica para un proyecto de scoring

Antes de construir un universo, medir la cobertura de cada salto para el período candidato (`ml-foundations/checks/check_traceability.py`, con un `--step` por tabla de la cadena y el canal como `--segment`). Si una parte relevante de las evaluaciones no se puede unir con su desempeño, el universo usable puede ser mucho más chico que el aparente, y además sesgado (por ejemplo, solo ciertos canales quedan trazados). Documentarlo en la ficha del modelo como limitación.
