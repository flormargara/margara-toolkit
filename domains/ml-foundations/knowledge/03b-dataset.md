# Dataset de modelado

El dataset une el universo con las features y es lo que el modelo ve. Es donde se pierden o se multiplican filas en un join y donde nace la diferencia entre cómo se entrena y cómo se predice. Se trata como un artefacto con contrato, no como un paso intermedio de un notebook.

## Una receta, tres universos

La **receta** une el universo (`entidad, fecha_corte` y el target) con cada bloque de features, con la información disponible hasta `fecha_corte`, y produce la matriz `X + target`.

- **Train, validación y scoring son la misma receta** con distinto universo de entrada. Nunca tres lógicas paralelas.
- El universo es un parámetro de la receta, no una tabla copiada adentro. Las fechas de corte y los bordes de partición se derivan del universo, no se escriben a mano.
- La lógica que construyó las filas de entrenamiento es la que reconstruye las filas de scoring. Así no aparece diferencia entre entrenamiento y producción (*train/serving skew*), y la extracción se hereda en lugar de reimplementarse.
- Si el target es multi-columna o tiene un catálogo, las columnas de target se generan desde ese catálogo, no se tipean a mano en varios lugares.
- Si las tablas fuente son grandes, la receta se corre una vez por fecha de corte, con el borde superior de cada tabla atado a la fecha de corte para no escanear la historia completa en cada corrida.

## Contrato de un bloque de features

Un bloque se puede ensamblar si cumple, verificado leyendo su SQL y corriéndolo sobre un corte:

| Propiedad | Se verifica |
|---|---|
| Parte del universo | Arranca del universo, no de una tabla propia |
| Preserva las filas | Una fila por `(entidad, fecha_corte)`; mismas filas que el universo |
| Devuelve su clave y sus features | Entidad, fecha de corte y columnas con nombre propio, sin colisiones con otros bloques |
| Respeta la fecha de corte | Nada posterior a `fecha_corte` entra al cálculo |

Un bloque que no cumple se devuelve a quien lo produjo con la propiedad que falla. No se arregla con un join especial en la receta.

## Sampling

Ver `01-universo-particiones.md`. El default es no samplear; si se samplea, solo train, con semilla o hash fijo dentro de la receta. Si el target es multi-columna, no existe "la fila negativa": se samplean filas enteras (por ejemplo, solo las que tienen todas las columnas del target en cero), nunca columnas del target por separado.

## Escala real

Si las features se validaron con una muestra, al correr la receta completa reconfirmar cobertura y distribuciones: faltantes inesperados o cardinalidades raras son hallazgos sobre los bloques, no datos para tapar.

## Gate del dataset

Obligatorio contra la matriz real, con veredicto explícito. `checks/check_dataset.py` lo automatiza.

| Chequeo | Condición |
|---|---|
| Sin duplicados de grano | 0 filas repetidas de `(entidad, fecha_corte)` en cada partición |
| Filas preservadas | Filas de la matriz = filas del universo, por partición |
| Target preservado | La suma (o la media) de cada columna de target coincide con la del universo |
| Sin superposición temporal | Ninguna fecha de corte de validación aparece en train |
| Faltantes esperados | Ninguna columna completamente vacía en una partición; los faltantes de cada columna no cambian de régimen entre particiones |
| Esquema idéntico | Mismas columnas, en el mismo orden, en train, validación y scoring (scoring sin target) |

Si un chequeo falla, la matriz no está lista: se corrige y se repite. No se documenta como pendiente.

## Contrato del dataset

Con el gate en verde, escribir el contrato (`templates/dataset-contract.md`): columnas y tipos, filas por partición, ubicación de cada exportación y cómo cargarla, sampling y semilla, veredictos del gate y la nota de que la receta es la que reutiliza la inferencia.

Los experimentos se comparan solo dentro de una misma versión del dataset (`04-modelado.md`).
