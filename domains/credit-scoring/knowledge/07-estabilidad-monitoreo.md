# Estabilidad y monitoreo

## PSI (Population Stability Index)

Compara la distribución del score (o de una variable) entre una población de referencia y una actual.

PSI = Σ (actual% − referencia%) · ln(actual% / referencia%)

| PSI | Lectura | Acción |
|---|---|---|
| < 0.10 | Estable | Ninguna |
| 0.10 – 0.25 | Cambio moderado | Investigar causas (canal, campaña, política) |
| > 0.25 | Cambio significativo | Revisar desempeño; evaluar recalibración o reentrenamiento |

- Usar los mismos cortes (deciles de la referencia) para ambas poblaciones.
- Bins vacíos rompen el logaritmo: aplicar un piso pequeño (por ejemplo 0.0001).
- El **CSI** es el mismo cálculo por variable; sirve para encontrar qué variable explica un PSI alto.
- `checks/psi.py` implementa ambos.

## En la validación

- PSI del score entre desarrollo y OOT.
- CSI de cada variable del modelo entre cohortes del período de desarrollo: descartar variables inestables antes de que lleguen al modelo final.

## En producción

Monitorear con frecuencia fija (mensual, típicamente):

| Qué | Cuándo se puede medir | Para qué |
|---|---|---|
| Volumen y tasa de aprobación | Inmediato | Cambios de canal o de política |
| PSI del score y CSI de variables | Inmediato | Cambios en la población |
| Tasa de faltantes por variable | Inmediato | Fuentes de datos rotas |
| Indicadores tempranos (first payment default, 30+ a 3 meses) | Pocos meses | Alerta temprana de desempeño |
| Gini / KS sobre cohortes maduras | Al cerrar la ventana de desempeño | Desempeño real del modelo |
| Calibración (PD estimada vs. observada) | Al cerrar la ventana | Necesidad de recalibrar |

Definir de antemano umbrales de alerta y quién actúa ante cada uno. Un monitoreo sin dueño ni umbrales no sirve.

## Recalibrar vs. reentrenar

- **Recalibrar** (ajustar el nivel de la PD) cuando el orden se mantiene pero cambió la tasa de malos promedio.
- **Reentrenar** cuando cae la discriminación, cambia la población de forma estructural o aparecen nuevas fuentes de datos.
