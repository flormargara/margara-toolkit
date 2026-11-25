# Features

## Ideación

Las features buenas salen de un mecanismo de negocio, no de recorrer tablas. El orden importa: primero el contexto, después los datos.

1. **Contexto antes que datos.** Acordar, en pocas preguntas: la decisión que apoya el modelo, la entidad y el universo, la fecha de corte o el período, y los mecanismos, reglas o ideas que ya tiene quien conoce el negocio. "No sé" es una respuesta válida: queda registrada como desconocida, no se inventa.
2. **El universo es fijo.** Una vez acordados el universo, el grano y la fecha de corte, no se rediseñan para mejorar la cobertura de una feature. Si los datos muestran un problema, se registra como alerta y se sigue con el universo acordado.
3. **Los valores de ejemplo no son parámetros.** Una fecha, filtro o umbral que aparece en un SQL o notebook de ejemplo se confirma antes de usarlo. Un artefacto existente es evidencia de sus tablas y joins, no el límite de la búsqueda.
4. **Ideas y mapa de dominios.** Cada idea se expresa como el mecanismo que intenta capturar ("los clientes que reducen el uso de la tarjeta antes de atrasarse"), sin afirmar todavía que los datos existen. Un mapa breve de dominios candidatos, en lenguaje de negocio, hace visible hacia dónde se busca.
5. **Ideas ancladas.** Una idea pasa a hipótesis solo cuando una fuente real la respalda: tabla y columnas verificadas, grano, transformación, ventana temporal y evidencia. Cada dominio explorado termina en una hipótesis anclada, una feature que ya existe o "sin idea aplicable". No se llenan cupos.
6. **Puntaje.** Cada hipótesis recibe de 1 a 5 en **potencial** (mecanismo, variabilidad, redundancia con otras) y en **factibilidad** (la fuente existe, el join funciona, hay cobertura en el universo, la temporalidad permite calcularla al corte). Puntaje = potencial × factibilidad. No hace falta el target: si se usa, es selección predictiva y vale lo de la sección "Selección de variables". Una temporalidad desconocida baja la factibilidad; nunca se presenta como validada.
7. **Selección y handoff.** Quien conoce el negocio ve la tabla completa y marca cada hipótesis como priorizada, idea o descartada. Las priorizadas pasan a construcción con todo lo necesario para no volver a descubrir nada (`templates/feature-handoff.md`).

## Fabricabilidad

Cada feature priorizada se construye como un bloque (`03b-dataset.md`, "Contrato de un bloque de features") y termina en un estado, con la razón:

| Estado | Cuándo |
|---|---|
| **Construida** | La consulta corre sobre todo el universo del período, preserva el grano y respeta la fecha de corte |
| **Reutilizada** | Es una columna existente (por ejemplo de un feature store) que cumple lo mismo |
| **No fabricable** | No corre, devuelve cero filas, multiplica o pierde filas sin arreglo, la temporalidad no se puede respetar, falta la columna, o los faltantes superan el umbral acordado |
| **Handoff incompleto** | El handoff tenía algo pendiente; vuelve a ideación |

Infinitos, denominadores cero, valores fuera de rango, varianza nula o una asociación muy fuerte con otra feature son alertas: no cambian el estado por sí solos, pero se reportan. Se sigue feature por feature aunque una falle. Las métricas de salud (filas, duplicados, faltantes, cardinalidad) se calculan sobre el universo completo; si se grafica con una muestra, la muestra es determinista y se registran su tamaño y semilla.

## Nombres

Formato: `<FUENTE>_<DOMINIO>_<OPERACION>_<DESCRIPCION>_<VENTANA>`, todo en mayúsculas, cinco segmentos separados por `_`, sin `-` ni segmentos vacíos. Por ejemplo, `BUR_TAR_CNT_CONSULTAS_6M`: cantidad de consultas al buró sobre tarjetas en los últimos 6 meses.

| Segmento | Regla |
|---|---|
| Fuente | Código corto del origen del dato (sistema propio, buró, proveedor) |
| Dominio | Código corto de la unidad de negocio o del producto |
| Operación | Del catálogo de abajo. Define el tipo de la variable |
| Descripción | Lo que mide, concatenado (`USOTOTAL`, `PRESTAMOSHIST`) |
| Ventana | `<n>H`, `<n>D` o `<n>M` (`24H`, `30D`, `6M`), o `NO` si no tiene ventana. `HIST` no es una ventana: va en la descripción |

Catálogo de operaciones:

| Tipo | Operaciones |
|---|---|
| Bandera (0/1) | `FLG` |
| Categórica | `CAT` |
| Numérica | `CNT` conteo, `SUM` suma, `MTO` monto, `AVG` promedio, `MED` mediana, `MOD` moda, `STD` desvío, `VAR` varianza, `MAX`, `MIN`, `PCT` porcentaje, `RAT` ratio, `DIF` diferencia, `TEN` tendencia, `TDC` tasa de cambio, `RCD` recencia en días, `RCM` recencia en meses, `IDX` índice, `ZSCORE` |

- Las claves (entidad, fecha de corte) y el target no llevan este formato.
- Una variable categórica publica `FLG` o `CAT` como operación aunque se haya calculado con otra agregación: un `MAX` de un segmento es `CAT`.
- Cada proyecto puede fijar su lista de fuentes y dominios válidos y agregar operaciones al catálogo. `checks/check_feature_names.py` valida los nombres y devuelve el tipo inferido de cada uno.

## Chequeo de datos antes de construir variables

- Verificar cada fuente contra lo pedido: cantidad de registros, duplicados por clave, que los joins no pierdan ni multipliquen filas.
- El significado de cada columna y de cada join se registra con su procedencia (`02-leakage.md`, "Observación y afirmación").
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
- El tipo de cada variable (numérica, categórica, bandera) se declara en la configuración o se deduce del segmento de operación del nombre (ver "Nombres"), nunca de un substring: buscar `cat` dentro del nombre convierte en categóricas a `indicator`, `duplicate` o `catalogo`.

## Modelos de árboles (GBM)

- Imponer restricciones de monotonicidad cuando la dirección del efecto es conocida.
- No depender de la importancia nativa: usar SHAP para explicar y para revisar que las variables top sean legítimas.
- Revisar la **concentración de la importancia**: si una variable explica una fracción muy grande del modelo, es frágil y es una señal de leakage (`checks/check_concentration.py`).
- Revisar estabilidad de las contribuciones en el tiempo, no solo la importancia promedio.

## Variables que requieren cuidado especial

- **Atributos sensibles y sus proxies**, según la regulación del dominio.
- **Variables construidas por el proceso o modelo vigente:** heredan su sesgo y pueden dejar de existir.
- **Variables declaradas por el usuario:** pueden manipularse una vez que se sabe que importan.
