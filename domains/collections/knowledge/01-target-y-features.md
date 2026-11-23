# Target, universo y features en cobranzas

## Universo

- **Una fila por cuenta y fecha de entrada al tramo** (por ejemplo, el día en que la cuenta llega a 1-2 días de atraso). La `fecha_corte` es ese día.
- Excluir cuentas que ya tienen otra obligación con más atraso, si la acción se define a nivel cliente.
- Si un cliente entra varias veces al tramo en el período, decidir si cada entrada es una fila (y entonces hacer split por cliente) o si se toma una por cliente con hash determinista.
- Separar o identificar cuentas en flujo de pago automático (débito) y fuera de él: tienen tasas de autocura muy distintas.

## Target

- **Pase de tramo:** la cuenta llega a un tramo de atraso peor (por ejemplo 31-60 días) dentro del horizonte (por ejemplo 30 días). Usar el **peor tramo alcanzado** en el horizonte.
- **Autocura:** la cuenta se regulariza sin gestión humana antes de cierto día. Medirlo **solo en el grupo de control** o en cuentas sin gestión, porque en las gestionadas no se puede separar la autocura del efecto de la gestión.
- Definir qué es "regularizar": pago mínimo, pago total del vencido o volver a 0 días de atraso.
- El horizonte tiene que haberse cumplido para todas las filas del universo de entrenamiento (madurez impuesta en la query).

## Features

Disponibles al momento de decidir (el día de entrada al tramo):

- Comportamiento de pago reciente: días de atraso históricos, cantidad de entradas previas en mora, tiempo desde la última mora, si pagó el mínimo o el total en los últimos ciclos.
- Uso de productos: consumos y utilización de la tarjeta, saldos y movimientos de cuentas, acreditación de sueldo.
- Deuda en el sistema (buró): saldos, cambios recientes, atrasos en otras entidades.
- Gestiones anteriores y su resultado (promesas cumplidas o incumplidas), **solo de episodios de mora previos**.

Leakage típico de cobranzas:

- Gestiones, contactos o promesas del **episodio actual**: ocurren después de la decisión.
- Fecha de primera gestión efectiva, días hasta el pago, estado de la cuenta al cierre del período.
- Asignación a agencia o equipo de gestión del episodio actual.

Agregar estos nombres al `forbidden_columns.txt` del proyecto.

## Baselines

Además de los baselines habituales, comparar siempre contra **la segmentación vigente** de cobranzas (por ejemplo, reglas por días de atraso y monto). El modelo tiene que mejorarla en la métrica que importa a la operación, no solo en AUC.

## Curvas de pago

Antes de fijar ventanas de espera, analizar las curvas de pago por rating: qué proporción de cada rating se regulariza sola en el día 3, 5, 10. La ventana de espera de cada segmento sale de ahí y de la capacidad operativa, no de una regla fija.
