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

## Observación y afirmación

Mucho leakage nace de leer mal una columna: una `fecha_alta` que en realidad es la fecha de la última modificación, un `monto` que ya incluye el resultado, una tabla que parece histórica y es una foto de hoy. Separar lo que se mide de lo que se afirma:

| | Qué es | Cómo se establece |
|---|---|---|
| **Observación** | Conteos, tipos, unicidad, rango de fechas, tasa de match de un join | Se mide con una consulta, en un alcance declarado (tabla, período, filtro) |
| **Afirmación** | Qué significa una columna, un código, un nulo o una relación entre tablas | Se declara con su procedencia: **confirmada** (documentación del dueño de la fuente o la persona que la conoce), **observada** (consistente con los datos, sin confirmar) o **ninguna** |

- El nombre de una columna no define su significado. Tampoco un tipo compatible, IDs que se superponen o un join que "matchea bastante" establecen que dos tablas se relacionan.
- Una afirmación **material** (cambia la fuente, el join, el universo, un filtro, una unidad o una moneda) sin confirmar bloquea ese paso: se pregunta o se busca evidencia, no se elige la interpretación más plausible.
- Una explicación de negocio que los datos no midieron se escribe como hipótesis, nombrando la evidencia que la confirmaría.
- Las cifras que se citan (porcentajes, rankings, máximos, totales) se calculan con código sobre datos guardados, no se leen de un gráfico ni se hacen de memoria.

Un join entre fuentes está listo cuando se registró: de quién es cada lado y cómo se genera, tipo y normalización de las claves, unicidad o multiplicación de filas en las claves, tasa de match y de no match en un alcance declarado, y si contradice algo ya establecido.

## Procedimiento

1. Construir un **diccionario de variables** con, para cada una: fuente, fecha de disponibilidad respecto del momento de la predicción, si existe en producción, la procedencia de su significado (ver arriba) y el enlace al SQL o al código que la calcula. Los nombres siguen el estándar de `03-features.md`.
2. Mantener una **lista de columnas prohibidas** del proyecto (`forbidden_columns.txt`, combinando la lista genérica de `checks/` con la del dominio) y correr `checks/check_leakage.py` sobre el código y la lista final de features.
3. Revisar manualmente las 10 variables más importantes del modelo: para cada una, explicar por qué estaría disponible en el momento de predecir.
4. Comparar la distribución de cada variable en desarrollo contra una muestra de producción reciente: si una variable no existe o se ve distinta en producción, hay un problema de disponibilidad.
