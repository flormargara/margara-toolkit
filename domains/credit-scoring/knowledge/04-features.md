# Features

## Binning y WoE

En scores interpretables (regresión logística sobre WoE) el binning es parte del modelo.

- Bins con al menos 5% de la población y una cantidad mínima de malos (por ejemplo 30) para que el WoE sea estable.
- **Monotonicidad:** el riesgo debe moverse en la dirección que el negocio espera (más ingresos, menos riesgo). Si el binning óptimo no es monótono, revisarlo: suele ser ruido o un problema de datos. Las excepciones (relaciones en U) se justifican por escrito.
- Faltantes como bin propio. El faltante suele ser informativo ("no tiene historial en buró").
- Valores especiales (por ejemplo -999, 0 por defecto) en bins separados, nunca mezclados con valores reales.
- Ajustar los cortes solo con train.

## Information Value (IV) como guía

| IV | Lectura |
|---|---|
| < 0.02 | Sin poder predictivo |
| 0.02 – 0.10 | Débil |
| 0.10 – 0.30 | Medio |
| 0.30 – 0.50 | Fuerte |
| > 0.50 | Sospechoso: revisar leakage (`03-leakage.md`) |

El IV mide poder individual; no reemplaza la selección multivariada.

## Selección de variables

- Eliminar variables con IV bajo, inestables en el tiempo (PSI por variable entre cohortes) o no disponibles en producción.
- Controlar colinealidad (correlación entre WoE, VIF). Entre dos variables muy correlacionadas, quedarse con la más estable y explicable.
- En regresión logística, los coeficientes sobre WoE deben tener todos el mismo signo. Un signo invertido indica colinealidad o un problema de datos.
- Preferir 10 a 20 variables bien entendidas a 100 variables marginales.

## Modelos de árboles (GBM)

- Imponer restricciones de monotonicidad cuando la dirección del riesgo es conocida.
- No depender de la importancia de variables nativa: usar SHAP para explicar y para revisar que las variables top sean legítimas.
- Revisar estabilidad de las contribuciones en el tiempo, no solo la importancia promedio.

## Variables que requieren cuidado especial

- **Variables sensibles y sus proxies** (ver `08-equidad-regulacion.md`).
- **Variables construidas por la política vigente** (por ejemplo, un score anterior): heredan su sesgo y pueden dejar de existir.
- **Variables declaradas por el solicitante** (ingresos, ocupación): pueden manipularse una vez que se sabe que importan.
