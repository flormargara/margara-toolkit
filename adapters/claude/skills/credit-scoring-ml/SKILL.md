---
name: credit-scoring-ml
description: Metodología para construir, validar y monitorear scores de riesgo crediticio (originación, new to credit, comportamental, upsell/downsell, PD, ratings). Usar al definir el target de default o hacer análisis de roll rate, armar el universo por fecha de solicitud y la ventana de desempeño, revisar leakage de crédito, construir variables WoE/IV o una regresión logística sobre WoE, calibrar la PD, construir ratings o puntos, fijar el punto de corte, analizar aprobados vs. solicitantes o reject inference, diseñar bandas de prueba o estrategias de límite, revisar la trazabilidad evaluación → desempeño o documentar un score. Incluye las prácticas generales de ML de ml-practices. Para cobranzas usar collections-ml.
---

# Scores de riesgo crediticio

Un score es un modelo de ML supervisado: aplica todas las prácticas generales de `ml-foundations/` y además lo específico de crédito de `references/`.

## Flujo

Seguir `references/00-flujo.md`, que indica para cada etapa el archivo general y el de crédito. Al empezar una etapa, leer primero el general y después el de crédito; no cargar todos de entrada.

| Etapa | General | Crédito |
|---|---|---|
| Trazabilidad | `ml-foundations/knowledge/08-trazabilidad.md` | `references/12-trazabilidad.md` |
| Problema y uso | `ml-foundations/knowledge/00-flujo.md` | `references/00-flujo.md` |
| Target de default, roll rate | — | `references/01-definicion-default.md` |
| Universo y particiones | `ml-foundations/knowledge/01-universo-particiones.md` | `references/02-particiones-validacion.md` |
| Leakage | `ml-foundations/knowledge/02-leakage.md` | `references/03-leakage.md` |
| Features, WoE/IV | `ml-foundations/knowledge/03-features.md` | `references/04-features.md` |
| Modelado, PD, puntos, corte | `ml-foundations/knowledge/04-modelado.md` | `references/05-modelado-calibracion.md` |
| Sesgo de selección, reject inference | `ml-foundations/knowledge/05-poblacion-y-sesgo.md` | `references/06-sesgo-seleccion.md` |
| Ratings | — | `references/10-ratings.md` |
| Monitoreo y promoción | `ml-foundations/knowledge/06-monitoreo.md` | `references/07-estabilidad-monitoreo.md` |
| Equidad, reason codes | — | `references/08-equidad-regulacion.md` |
| Experimentación, bandas de prueba, límites | `ml-foundations/knowledge/07-experimentacion.md` | `references/11-experimentacion.md` |
| Documentación | `ml-foundations/knowledge/09-documentacion.md` | `references/09-documentacion.md` |

Para la forma de trabajar, seguir `shared/agent-workflow.md`.

## Reglas que no se negocian

Todas las de la skill `ml-practices` (validación out-of-time, sin variables posteriores a la decisión, elegibilidad idéntica, transformaciones y sampling solo en train, árbitro intacto, baselines y ablaciones, recalibrar después de rebalancear, margen mínimo para reemplazar un modelo, grupo de control si la acción cambia el resultado, evidencia en cohortes maduras). Además, en crédito:

1. El default se define con análisis de roll rate y se acuerda con riesgo; no se inventa.
2. Ninguna cohorte entra al universo sin haber cumplido la ventana de desempeño.
3. AUC > 0.90 o una variable con IV > 0.5 se tratan como sospecha de leakage.
4. Siempre hay un baseline de regresión logística sobre WoE y otro con la política de riesgo vigente.
5. Se registra el score de todos los solicitantes, incluidos los rechazados por reglas.
6. Los ratings se validan en una segunda muestra con un error de calibración por rating acotado.
7. El punto de corte lo decide el dueño del riesgo; el modelo entrega la tabla de opciones.

Cuando una regla impide lo que se pidió, decirlo explícitamente. Cuando la documentación de un repositorio contradice al código, seguir el código y avisar.

## Chequeos ejecutables

Los chequeos están en `ml-foundations/checks/`. La lista de patrones de leakage de crédito y cobranzas está en `patterns/forbidden_columns.example.txt`.

| Chequeo | Uso |
|---|---|
| Integridad del universo | `python3 ml-foundations/checks/check_universe.py universo.csv --horizon-days <ventana en días> --last-data-date AAAA-MM-DD --id-col <id>` |
| Leakage | `python3 ml-foundations/checks/check_leakage.py --features lista.txt`. Usa `forbidden_columns.txt` de la raíz del proyecto; si no existe, proponer crearlo combinando `ml-foundations/checks/forbidden_columns.example.txt` y `patterns/forbidden_columns.example.txt` |
| Concentración de importancia | `python3 ml-foundations/checks/check_concentration.py importancias.csv` |
| Estabilidad | `python3 ml-foundations/checks/psi.py ref.csv act.csv --column score`, o `--all-numeric` para CSI |

## Entregables

Al cerrar un score, completar `templates/model-card.md` y `templates/checklist-validacion.md` (versiones de crédito) en el repositorio del proyecto. Cada número reportado indica de qué partición sale.
