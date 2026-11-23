# Features

## Chequeo de datos antes de construir variables

- Verificar cada fuente contra lo pedido: cantidad de registros, duplicados por clave, que los joins no pierdan ni multipliquen filas.
- Para cada campo continuo, un resumen de ocho números: faltantes, mínimo, p1, Q1, mediana, Q3, p99, máximo.
- Que cada código tenga definición y que las distribuciones tengan sentido de negocio.

## Faltantes, ceros y extremos

- **La semántica del faltante depende de la variable.** Contadores y montos faltantes suelen significar "no hubo" y van a 0. Edades, porcentajes y ratios faltantes son faltantes de verdad y se tratan como categoría propia.
- **Población mínima.** Eliminar variables con menos de 2-3% de valores informados (no faltantes, no cero, no valor por defecto), salvo excepción justificada.
- **Capping en p99 y flooring en p1** para variables continuas (el flooring, sobre todo para ratios y variables que pueden ser negativas). Los percentiles se calculan con train.

## Binning y WoE

En scores interpretables (regresión logística sobre WoE) el binning es parte del modelo.

- Bins con al menos 5% de la población y una cantidad mínima de malos (por ejemplo 30) para que el WoE sea estable.
- **Monotonicidad:** el riesgo debe moverse en la dirección que el negocio espera. Si el binning óptimo no es monótono, revisarlo: suele ser ruido o un problema de datos. Las excepciones (relaciones en U) se justifican por escrito.
- Agrupaciones intuitivas antes que puramente estadísticas: el 0 en un bin propio, faltantes como bin propio, valores especiales (por ejemplo −999) separados.
- Se pueden unir bins o categorías con WoE muy parecido.
- Ajustar los cortes solo con train y, si el target es binario con indeterminados, usar solo buenos y malos.

## Information Value (IV) como guía

| IV | Lectura |
|---|---|
| < 0.02 | Sin poder predictivo |
| 0.02 – 0.10 | Débil |
| 0.10 – 0.30 | Medio |
| 0.30 – 0.50 | Fuerte |
| > 0.50 | Sospechoso: revisar leakage (`03-leakage.md`) |

El IV mide poder individual; no reemplaza la selección multivariada.

## Estabilidad por período

Una variable sirve si es predictiva **y** estable en el tiempo. Los filtros se evalúan período a período (por ejemplo por mes de snapshot), no solo sobre la muestra total, y la inestabilidad se acumula dando más peso a los períodos recientes:

| Filtro | Falla en un período si… |
|---|---|
| Nulos | La proporción de nulos supera el umbral (por ejemplo 30%) |
| Concentración | Más del 99% de los valores están en la moda |
| Variabilidad | El coeficiente de variación (numéricas) o la entropía normalizada (categóricas) es muy bajo |
| Estabilidad de distribución | PSI, cambio de media o categorías nuevas superan el umbral |
| IV en rango | El IV del período cae debajo de 0.02 o supera 0.5 |
| Relación con el target | El AUC univariado se aleja de la historia más de un delta (por ejemplo 0.05), o **la dirección de la relación se invierte** |
| Correlación estable | Dos variables están muy correlacionadas (φk > 0.9) de forma estable; se conserva una |

## Selección de variables

- Documentar el **embudo** con la cantidad que sobrevive a cada paso: candidatas → filtro manual de leakage → nulos → varianza → estabilidad → correlación → selección multivariada (Boruta/SHAP, eliminación recursiva) → finales. Va en la ficha del modelo.
- Eliminar variables no disponibles en producción.
- Controlar colinealidad (correlación entre WoE, VIF). En regresión logística, apuntar a VIF < 2 y justificar las excepciones. Entre dos variables muy correlacionadas, quedarse con la más estable y explicable.
- En regresión logística, los coeficientes sobre WoE deben tener todos el mismo signo y coincidir con el sentido de negocio. Un signo invertido indica colinealidad o un problema de datos.
- Preferir 10 a 20 variables bien entendidas a 100 variables marginales. Seleccionar por grupo de fuentes ayuda a que el modelo no dependa de una sola.

## Modelos de árboles (GBM)

- Imponer restricciones de monotonicidad cuando la dirección del riesgo es conocida.
- No depender de la importancia de variables nativa: usar SHAP para explicar y para revisar que las variables top sean legítimas.
- Revisar la **concentración de la importancia**: si una variable explica una fracción muy grande del modelo, es frágil y es una señal de leakage (`checks/check_concentration.py`).
- Revisar estabilidad de las contribuciones en el tiempo, no solo la importancia promedio.

## Variables que requieren cuidado especial

- **Variables sensibles y sus proxies** (ver `08-equidad-regulacion.md`).
- **Variables construidas por la política vigente** (por ejemplo, un score anterior): heredan su sesgo y pueden dejar de existir.
- **Variables declaradas por el solicitante** (ingresos, ocupación): pueden manipularse una vez que se sabe que importan.
