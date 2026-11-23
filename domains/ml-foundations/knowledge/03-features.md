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

### Dos modos

Seleccionar variables mirando el target es una búsqueda, igual que buscar hiperparámetros. Separar los dos modos:

| Modo | Criterios | Dónde corre |
|---|---|---|
| **Sin target** | Cobertura, varianza casi nula, leakage estructural (usa información posterior al corte, deriva del evento que define el target, es un identificador), redundancia (correlación de rangos, duplicados), estabilidad de la distribución | En la etapa de features, sobre todo el universo. Nunca abre la columna del target |
| **Predictiva** | Poder predictivo en rango (IV, AUC univariado), relación con el target estable y sin inversión, Boruta, SHAP, eliminación recursiva, L1, importancia por permutación | Solo dentro de train. Si hay un loop de búsqueda con folds, se reajusta en cada fold. Nunca mira la validación final |

- Los umbrales del modo sin target se proponen y se confirman antes de aplicarlos: cambian qué set queda.
- Una selección predictiva hecha sobre todo el train antes de la búsqueda deja limpio el árbitro, pero hace optimista la métrica de CV posterior. Decirlo cuando se reporta esa métrica.
- Una selección predictiva es un experimento más del leaderboard (`04-modelado.md`): su base es el líder vigente, su cambio es el set de variables, y se evalúa una vez contra el árbitro.
- Elegir la cantidad de variables mirando el conjunto de test lo convierte en conjunto de selección (`01-universo-particiones.md`).
- No hay método por defecto. Cada uno tiene su trampa: la importancia por permutación se diluye entre variables correlacionadas, L1 es sensible a la escala, stability selection necesita fijar el umbral de frecuencia, la eliminación recursiva depende del modelo base.

### Embudo

- Documentar el **embudo** con la cantidad que sobrevive a cada paso, marcando qué pasos usan el target: candidatas → filtro manual de leakage → nulos → varianza → estabilidad de distribución → correlación (sin target) → poder predictivo y relación con el target → selección multivariada (Boruta/SHAP, eliminación recursiva) (predictivos) → finales.
- Eliminar variables no disponibles en producción.
- Controlar colinealidad. Entre dos variables muy correlacionadas, quedarse con la más estable y explicable.
- Preferir pocas variables bien entendidas a muchas marginales. Seleccionar por grupo de fuentes ayuda a que el modelo no dependa de una sola.
- Las categóricas de alta cardinalidad se agrupan (categorías raras en "otros") con frecuencias calculadas en train.
- El tipo de cada variable (numérica, categórica, bandera) se declara en la configuración o se deduce de un token completo del nombre (por ejemplo `_cat_`), nunca de un substring: buscar `cat` dentro del nombre convierte en categóricas a `indicator`, `duplicate` o `catalogo`.

## Modelos de árboles (GBM)

- Imponer restricciones de monotonicidad cuando la dirección del efecto es conocida.
- No depender de la importancia nativa: usar SHAP para explicar y para revisar que las variables top sean legítimas.
- Revisar la **concentración de la importancia**: si una variable explica una fracción muy grande del modelo, es frágil y es una señal de leakage (`checks/check_concentration.py`).
- Revisar estabilidad de las contribuciones en el tiempo, no solo la importancia promedio.

## Variables que requieren cuidado especial

- **Atributos sensibles y sus proxies**, según la regulación del dominio.
- **Variables construidas por el proceso o modelo vigente:** heredan su sesgo y pueden dejar de existir.
- **Variables declaradas por el usuario:** pueden manipularse una vez que se sabe que importan.
