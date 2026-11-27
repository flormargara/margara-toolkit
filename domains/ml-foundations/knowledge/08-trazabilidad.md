# Trazabilidad

Sin poder reconstruir qué predicción llevó a qué decisión y qué resultado tuvo esa decisión, no se puede hacer backtest, medir el modelo en producción ni entrenar la versión siguiente. La trazabilidad es un requisito previo del modelado, no una tarea de datos aparte.

## La cadena

```
entrada → predicción → decisión → acción → resultado
```

Cada salto necesita una **clave única y estable** que esté en ambos lados. Problemas típicos que rompen la cadena:

- La clave del lado destino no existe o tiene otro formato.
- Una tabla tiene menos registros que otra que debería contener los mismos (registros que se pierden en una sincronización).
- La clave cambia de significado en una fecha y las consultas necesitan condiciones distintas por período.
- Columnas de identificación sin parsear dentro de un JSON.
- Deduplicaciones no deterministas (`row_number()` sobre una clave que no es única en una de las tablas), que hacen que la misma consulta devuelva resultados distintos.
- Fechas con formato incorrecto en tablas de origen.

### La cadena de consumo

La cadena no termina en la tabla de predicciones. También es parte de la trazabilidad lo que pasa con la salida después:

- **Quién la recibe:** sistema, proceso o equipo, y con qué identificador la toma.
- **Por qué medio:** tabla, archivo, API, cola de mensajes; con su ubicación exacta.
- **Qué pasa si la entrega falla:** si hay reintento o reenvío, si se avisa y a quién, y si el consumidor decide con la salida anterior o sin modelo.
- **Confirmación de recepción:** cuántos registros se enviaron y cuántos se tomaron. Una diferencia es un salto roto de la cadena, igual que un join que pierde filas.

Se documenta en la ficha del modelo ("Consumo y respaldo").

## Qué registrar en cada predicción

- Identificadores de la entidad y del evento.
- Predicción, banda o grupo, y **versión del modelo**.
- **Versión de la regla, política o campaña** que tomó la decisión.
- Resultado de cada regla aplicada y motivo de exclusión.
- Identificadores de las fuentes externas consultadas.
- La predicción de toda la población, incluida la que las reglas excluyen (ver `05-poblacion-y-sesgo.md`).
- Variante de experimento, si aplica.

## Medir la trazabilidad como un indicador

Para cada salto, calcular qué porcentaje de registros encuentra su par en la tabla siguiente, por período y por segmento. Publicarlo como indicador de calidad con un umbral, y tratar una caída como un incidente.

Ante un problema, documentar:

- Período y volumen afectado.
- Si la corrección es retroactiva o solo hacia adelante.
- Quién lo detecta, quién lo corrige y por qué canal se notifica.
- Qué modelos, tableros o análisis quedan invalidados mientras tanto.

## Consecuencia práctica

Antes de construir un universo, medir la cobertura de cada salto para el período candidato. Si una parte relevante de los registros no se puede unir con su resultado, el universo usable puede ser mucho más chico que el aparente, y además sesgado (por ejemplo, solo ciertos canales quedan trazados). Documentarlo como limitación.
