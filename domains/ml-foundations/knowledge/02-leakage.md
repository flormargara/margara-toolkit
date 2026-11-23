# Data leakage

Leakage es usar información que no estaría disponible en el momento de la predicción. Produce modelos que se ven excelentes en desarrollo y fallan en producción.

## Señales de alarma

- Desempeño sospechosamente alto para la dificultad del problema.
- Una sola variable que explica casi todo el modelo, sin explicación causal (`checks/check_concentration.py`).
- Gran diferencia de desempeño entre desarrollo y producción o shadow mode.
- Variables con nombres de resultado o de estado final.

## Fuentes típicas

| Fuente | Ejemplo | Cómo evitarla |
|---|---|---|
| Variables posteriores a la predicción | Resultado, estado final, acciones tomadas después | Fecha de corte estricta = momento de la predicción |
| Tablas "foto actual" | Datos maestros consultados hoy, no a la fecha del snapshot | Usar versiones históricas (snapshot a la fecha) |
| Variables de proceso | Consecuencias de la decisión que el modelo apoya | Excluir |
| Agregados con ventana mal cortada | "Promedio de los últimos 6 meses" calculado hasta hoy | Calcular siempre hasta el corte |
| Target encoding sin out-of-fold | Promedio del target por categoría usando toda la muestra | Calcular dentro de cada fold de train |
| Duplicados entre particiones | Misma entidad en train y validación | Split por grupo |
| Transformaciones con toda la muestra | Medias de imputación calculadas incluyendo la validación | Ajustar solo con train |
| Datos corregidos después | Registros reprocesados o enriquecidos con información posterior | Usar la versión disponible en la fecha de corte |

## Procedimiento

1. Construir un **diccionario de variables** con, para cada una: fuente, fecha de disponibilidad respecto del momento de la predicción y si existe en producción.
2. Mantener una **lista de columnas prohibidas** del proyecto (`forbidden_columns.txt`, combinando la lista genérica de `checks/` con la del dominio) y correr `checks/check_leakage.py` sobre el código y la lista final de features.
3. Revisar manualmente las 10 variables más importantes del modelo: para cada una, explicar por qué estaría disponible en el momento de predecir.
4. Comparar la distribución de cada variable en desarrollo contra una muestra de producción reciente: si una variable no existe o se ve distinta en producción, hay un problema de disponibilidad.
