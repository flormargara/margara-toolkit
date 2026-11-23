# Features en crédito: WoE, IV y binning

Aplica todo `ml-foundations/knowledge/03-features.md`: semántica de faltantes, capping, estabilidad por período, embudo de selección, SHAP y concentración. Acá está lo propio de los scores interpretables de crédito.

## Binning y WoE

En scores interpretables (regresión logística sobre WoE) el binning es parte del modelo. El WoE de un bin es el logaritmo del cociente entre la proporción de buenos y la de malos en ese bin.

- Bins con al menos 5% de la población y una cantidad mínima de malos (por ejemplo 30) para que el WoE sea estable.
- **Monotonicidad:** el riesgo debe moverse en la dirección que el negocio espera (más ingresos, menos riesgo). Si el binning óptimo no es monótono, revisarlo: suele ser ruido o un problema de datos. Las excepciones (relaciones en U) se justifican por escrito.
- Agrupaciones intuitivas antes que puramente estadísticas: el 0 en un bin propio, faltantes como bin propio, valores especiales separados.
- Se pueden unir bins o categorías con WoE muy parecido.
- Ajustar los cortes solo con train y, si hay indeterminados, usar solo buenos y malos.
- `checks/check_woe_bins.py` verifica la tabla de binning: bins sin buenos o sin malos, tamaño y malos mínimos, monotonía e IV fuera de rango.

## Information Value (IV)

| IV | Lectura |
|---|---|
| < 0.02 | Sin poder predictivo |
| 0.02 – 0.10 | Débil |
| 0.10 – 0.30 | Medio |
| 0.30 – 0.50 | Fuerte |
| > 0.50 | Sospechoso: revisar leakage (`03-leakage.md`) |

- El IV mide poder individual; no reemplaza la selección multivariada.
- En el filtro de estabilidad por período (ver `ml-foundations/knowledge/03-features.md`), el "poder predictivo en rango" se mide con el IV de cada período: entre 0.02 y 0.5.
- Las variables con IV extremadamente alto pueden anular la contribución de las demás; requieren atención especial.

## Regresión logística sobre WoE

- Coeficientes con el mismo signo y coherentes con el sentido de negocio. Un signo invertido indica colinealidad o un problema de datos.
- VIF < 2 como guía; justificar las excepciones.
- No descartar automáticamente variables con p-valor > 0.05 si tienen sentido de negocio; documentar el criterio.
- Seleccionar por grupo de fuentes (buró, comportamiento interno, datos de la solicitud) para que el score no dependa de una sola.

## Fuentes de variables habituales

| Fuente | Ejemplos |
|---|---|
| Buró y central de riesgos | Deuda total y por entidad, peor situación, consultas recientes, antigüedad en el sistema |
| Comportamiento interno | Pagos y atrasos en productos propios, utilización de la tarjeta, saldos y movimientos de cuentas |
| Ingresos | Declarados, estimados por modelo o inferidos de acreditaciones |
| Solicitud | Producto, monto, plazo, canal (cuidado: algunos son decisiones de la entidad) |
| Datos alternativos | Transaccionales y de otras empresas del grupo, útiles para new to credit |

Las variables declaradas por el solicitante (ingresos, ocupación) pueden manipularse una vez que se sabe que importan.
