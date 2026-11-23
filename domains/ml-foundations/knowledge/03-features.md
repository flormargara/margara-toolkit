# Features

## Chequeo de datos antes de construir variables

- Verificar cada fuente contra lo pedido: cantidad de registros, duplicados por clave, que los joins no pierdan ni multipliquen filas.
- Para cada campo continuo, un resumen de ocho números: faltantes, mínimo, p1, Q1, mediana, Q3, p99, máximo.
- Que cada código tenga definición y que las distribuciones tengan sentido de negocio.

## Faltantes, ceros y extremos

- **La semántica del faltante depende de la variable.** Contadores y montos faltantes suelen significar "no hubo" y van a 0. Edades, porcentajes y ratios faltantes son faltantes de verdad y se tratan como tales (categoría propia, imputación o manejo nativo del modelo).
- **Población mínima.** Eliminar variables con muy pocos valores informados (por ejemplo menos de 2-3% no faltante, no cero, no valor por defecto), salvo excepción justificada.
- **Capping en p99 y flooring en p1** para variables continuas cuando el modelo es sensible a extremos. Los percentiles se calculan con train.
- Valores especiales (por ejemplo −999) separados de los valores reales.

## Estabilidad por período

Una variable sirve si es predictiva **y** estable en el tiempo. Los filtros se evalúan período a período (por ejemplo por mes de snapshot), no solo sobre la muestra total, y la inestabilidad se acumula dando más peso a los períodos recientes:

| Filtro | Falla en un período si… |
|---|---|
| Nulos | La proporción de nulos supera el umbral (por ejemplo 30%) |
| Concentración | Más del 99% de los valores están en la moda |
| Variabilidad | El coeficiente de variación (numéricas) o la entropía normalizada (categóricas) es muy bajo |
| Estabilidad de distribución | PSI, cambio de media o categorías nuevas superan el umbral |
| Poder predictivo en rango | La asociación univariada con el target cae debajo de un mínimo o supera un máximo sospechoso |
| Relación con el target | El AUC univariado (o la correlación) se aleja de la historia más de un delta, o **la dirección de la relación se invierte** |
| Correlación estable | Dos variables están muy correlacionadas (por ejemplo φk > 0.9) de forma estable; se conserva una |

## Selección de variables

- Documentar el **embudo** con la cantidad que sobrevive a cada paso: candidatas → filtro manual de leakage → nulos → varianza → estabilidad → correlación → selección multivariada (Boruta/SHAP, eliminación recursiva) → finales.
- Eliminar variables no disponibles en producción.
- Controlar colinealidad. Entre dos variables muy correlacionadas, quedarse con la más estable y explicable.
- Preferir pocas variables bien entendidas a muchas marginales. Seleccionar por grupo de fuentes ayuda a que el modelo no dependa de una sola.
- Las categóricas de alta cardinalidad se agrupan (categorías raras en "otros") con frecuencias calculadas en train.

## Modelos de árboles (GBM)

- Imponer restricciones de monotonicidad cuando la dirección del efecto es conocida.
- No depender de la importancia nativa: usar SHAP para explicar y para revisar que las variables top sean legítimas.
- Revisar la **concentración de la importancia**: si una variable explica una fracción muy grande del modelo, es frágil y es una señal de leakage (`checks/check_concentration.py`).
- Revisar estabilidad de las contribuciones en el tiempo, no solo la importancia promedio.

## Variables que requieren cuidado especial

- **Atributos sensibles y sus proxies**, según la regulación del dominio.
- **Variables construidas por el proceso o modelo vigente:** heredan su sesgo y pueden dejar de existir.
- **Variables declaradas por el usuario:** pueden manipularse una vez que se sabe que importan.
