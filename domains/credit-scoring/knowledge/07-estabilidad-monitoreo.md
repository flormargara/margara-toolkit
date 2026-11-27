# Monitoreo de scores de crédito

Aplica todo `ml-foundations/knowledge/06-monitoreo.md`: PSI/CSI, tres capas, drift de importancias, presupuesto de drift, recalibrar vs. reentrenar, regla de promoción champion / challenger / recalibrado con margen mínimo y comunicación con evidencia. Acá está lo propio de crédito.

## Qué monitorear en cada capa

| Capa | En crédito |
|---|---|
| Negocio | Tasa de malos esperada vs. observada por rating; distribución por rating; tasa de aprobación; motivos de rechazo; adopción de la oferta por rating; montos y plazos otorgados |
| Modelo | Gini/KS por cohorte de originación madura; PSI del score; CSI de las variables; drift de importancias |
| Datos | Respuesta de los burós (tiempos, errores, faltantes); frescura de las tablas de cartera; categorías nuevas en productos y canales |

## Cohortes de originación

- Mirar cada cohorte mensual de originación durante toda la vida del modelo: tasa de malos por decil o rating cuando la cohorte madura. "¿Sigue ordenando o está mezclando?"
- **Indicadores tempranos** para no esperar la ventana completa: first payment default, 30+ a 3 meses, 60+ a 6 meses. Validar en el desarrollo que estos indicadores ordenan igual que el target final.

## Comportamentales y límites

Si el score decide aumentos o reducciones de límite, la acción cambia el desempeño (más línea, más exposición). Medir el modelo sobre un grupo de control sin cambio de límite y comparar estrategias de límite con experimentos (ver `11-experimentacion.md`).

## Recalibración en crédito

- Cambios de ciclo económico o de política mueven el nivel de mora sin cambiar el orden: recalibrar la PD o los cortes de rating antes que reentrenar.
- Comparar champion, recalibrado y challenger con el **error de calibración por rating** además de Gini y KS. Si la spec fija KS como métrica principal, `promotion.py --metric ks --secondary-tolerance <tol>` decide por KS sin dejar caer el Gini.

## Revisión periódica

Además del monitoreo continuo, una revisión completa del desempeño al menos una vez por año, documentada en la ficha del modelo.
