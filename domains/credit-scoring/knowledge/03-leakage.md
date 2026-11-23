# Data leakage

Leakage es usar información que no estaría disponible en el punto de decisión. Produce modelos que se ven excelentes en desarrollo y fallan en producción.

## Señales de alarma

- AUC mayor a 0.90 en un score de originación. No es imposible, pero hay que demostrar que no hay leakage antes de creerlo.
- Una sola variable con IV mayor a 0.5 o que explica casi todo el modelo.
- Gran diferencia de desempeño entre desarrollo y producción o shadow mode.
- Variables con nombres de resultado: `mora`, `atraso`, `castigo`, `estado_final`, `dias_vencido`, `cobranza`, `recupero`, `refinanciado`.

## Fuentes típicas

| Fuente | Ejemplo | Cómo evitarla |
|---|---|---|
| Variables posteriores a la decisión | Saldo, atraso o pagos del propio préstamo | Fecha de corte estricta = punto de decisión |
| Tablas "foto actual" | Datos de buró o del cliente consultados hoy, no a la fecha de la solicitud | Usar versiones históricas (snapshot a la fecha) |
| Variables de proceso | Fecha de desembolso, monto aprobado, oferta final, analista asignado | Excluir: son consecuencia de la decisión |
| Agregados con ventana mal cortada | "Promedio de atraso últimos 6 meses" calculado hasta hoy | Calcular siempre hasta el punto de decisión, sin incluirlo si no estaba disponible |
| Target encoding sin out-of-fold | Promedio del target por categoría usando toda la muestra | Calcular dentro de cada fold de train |
| Duplicados entre particiones | Misma persona o solicitud en train y OOT | Split por grupo |
| Imputación con toda la muestra | Medias calculadas incluyendo el OOT | Ajustar solo con train |

## Procedimiento

1. Construir un **diccionario de variables** con, para cada una: fuente, fecha de disponibilidad respecto del punto de decisión y si existe en producción.
2. Mantener una **lista de columnas prohibidas** del proyecto (`forbidden_columns.txt`) y correr `checks/check_leakage.py` sobre el código y la lista final de features.
3. Revisar manualmente las 10 variables más importantes del modelo: para cada una, explicar por qué estaría disponible en el momento de decidir.
4. Comparar la distribución de cada variable en desarrollo contra una muestra de producción reciente: si una variable no existe o se ve distinta en producción, hay un problema de disponibilidad.
