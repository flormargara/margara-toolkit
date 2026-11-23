# Modelos de cobranzas: flujo y diseño

Un modelo de cobranzas no predice quién va a pagar en abstracto: decide **a quién gestionar, cuándo y por qué canal**, sobre cuentas que ya están en mora. Eso cambia tres cosas respecto de un score de originación: el resultado depende de la acción tomada, el horizonte es corto y el costo de gestión es parte del problema.

Este dominio complementa a `credit-scoring`: target, particiones, leakage, features, ratings y monitoreo siguen las mismas reglas (`domains/credit-scoring/knowledge/`). Acá está lo específico.

## Etapas

| # | Etapa | Punto de control |
|---|---|---|
| 1 | Problem framing | Tramo de entrada, horizonte, evento, acción por segmento y métrica de éxito acordados con cobranzas |
| 2 | Análisis del modelo o la segmentación vigente | Performance actual medida sobre el grupo de control; curvas de pago por segmento |
| 3 | Universo y target | Universo por fecha de entrada en mora; `check_universe.py` en verde |
| 4 | Features y EDA | Estabilidad temporal; variables de gestión solo si están disponibles al momento de decidir |
| 5 | Modelado y ratings | Baselines (incluida la segmentación vigente), ratings con error de calibración acotado |
| 6 | Backtest | Modelo corrido sobre el día o mes anterior con datos congelados y validado con el negocio |
| 7 | Piloto | Muestreo estratificado, ventanas por segmento configuradas, monitoreo diario de los primeros días |
| 8 | Integración | Pipelines de entrenamiento, inferencia y monitoreo; envío a la operación con alertas ante fallas |
| 9 | Monitoreo | Mensual: desempeño sobre control, impacto contra control, costo de gestión |

## Problem framing

Responder por escrito:

- **Tramo de entrada:** desde qué atraso entra una cuenta al universo (por ejemplo, mora leve de 1 a 2 días) y si se excluye a quien tiene otra cuenta con más atraso.
- **Evento y horizonte:** qué se predice y en cuánto tiempo. Ejemplos: pasar a mora moderada (31-60 días) en 30 días; curarse sin gestión (autocura) antes de cierto día.
- **Productos:** tarjeta y préstamo pueden necesitar modelos separados o una variable de producto; las dinámicas de pago son distintas. Lo mismo para cuentas en flujo de pago automático y fuera de él.
- **Acción por segmento:** qué se hace con cada grupo de ratings. Ejemplo:

| Segmento | Acción |
|---|---|
| Riesgo bajo (alta autocura) | Solo canales digitales automáticos; sin gestión humana durante una ventana de espera larga |
| Riesgo medio | Recordatorios digitales intensivos; gestión humana después de una ventana corta |
| Riesgo alto | Gestión humana e intensiva desde los primeros días |

- **Métrica de éxito de negocio:** por ejemplo, reducir en un X% el pase de tramo, concentrar la gestión humana en los segmentos de riesgo alto o reducir contactos innecesarios a clientes que se curan solos.
- **Restricciones operativas:** capacidad del equipo de gestión, horarios, canales disponibles, días hábiles.

## Diferencias con originación

| Aspecto | Originación | Cobranzas |
|---|---|---|
| Efecto de la acción | La decisión de aprobar define quién tiene target | La gestión cambia el resultado que se intenta predecir |
| Horizonte | Meses | Días o semanas |
| Frecuencia de scoreo | Por solicitud | Diaria, sobre todas las cuentas que entran al tramo |
| Datos más útiles | Buró, ingresos, historial | Comportamiento reciente de pago, uso de cuentas, historial de mora y gestiones anteriores |
| Costo del error | Pérdida por aprobar mal / negocio perdido por rechazar | Pase de tramo por no gestionar / costo y molestia por gestionar a quien se curaba solo |

## Entrenar solo con el grupo de control

Es la regla central del dominio. Una vez que el modelo decide a quién se gestiona, el resultado de las cuentas tratadas refleja la gestión y no el riesgo original. Si el modelo se reentrena con esos casos, aprende de su propio efecto y con el tiempo subestima el riesgo de los segmentos mejor gestionados.

- El reentrenamiento usa **solo cuentas del grupo de control**, cuyo resultado no está afectado por la gestión guiada por el modelo.
- Por eso el control tiene que ser lo bastante grande en cada rating para alimentar el reentrenamiento, no solo para medir impacto. Revisar el tamaño con este doble objetivo (ver `domains/credit-scoring/knowledge/11-experimentacion.md`).
- Antes de que exista un control propio, el primer modelo se entrena con la historia previa al modelo y se documenta qué gestión recibieron esas cuentas.

## Grupo de control

- Aleatorio y escalonado por rating (por ejemplo 3%, 5% y 8% de menor a mayor riesgo), persistente entre corridas y con exclusiones documentadas (por ejemplo, deudas por encima de un monto o un tope mensual de exposición del control).
- Una cuenta del control no recibe la acción guiada por el modelo, pero sí lo que la política exija como mínimo (por ejemplo, avisos regulatorios). Documentar qué recibe exactamente.

## Métricas

**Del modelo (sobre el grupo de control):** AUC, KS, tasa de pase por rating vs. esperada (error de calibración acotado, por ejemplo ±5 puntos), estabilidad por cohorte.

**De impacto (tratamiento vs. control, con ITT):**
- Tasa de pase de tramo y tasa de autocura por rating.
- Recupero o monto regularizado.
- Días hasta la regularización.

**Operativas y de costo:**
- Proporción de la gestión humana concentrada en los segmentos de riesgo alto.
- Contactos por cuenta y costo de gestión por segmento.
- Primera gestión efectiva: fecha y tipo de contacto (promesa de pago, contacto con el titular, contacto con terceros).

Evitar métricas mal nombradas: el cociente "tasa de agravamiento del control / del tratado" mide el **impacto** de la gestión, no la discriminación del modelo.

## Operación

- **Inferencia diaria** en días hábiles, a una hora fija compatible con la operación de cobranzas.
- **Entrenamiento y monitoreo mensuales**, con el reentrenamiento sujeto a la regla champion / challenger / recalibrado (ver `domains/credit-scoring/knowledge/07-estabilidad-monitoreo.md`).
- **Integración con la operación** (archivo, API o tabla): alertas ante dataset vacío, caída de volumen, fallas de lectura, discrepancias en joins o fallas de envío, con un procedimiento de reenvío.
- **Tablero mensual** que cruce la salida del modelo con las gestiones realizadas y su costo, con fechas de actualización y ventanas definidas.
