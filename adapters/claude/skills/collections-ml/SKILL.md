---
name: collections-ml
description: Metodología para modelos de cobranzas y mora (segmentación de mora temprana, pase de tramo, autocura, priorización de gestión). Usar al definir el problem framing de un modelo de cobranzas, el universo por fecha de entrada en mora, el target de pase de tramo o autocura, las ventanas de espera y acciones por segmento, el grupo de control, el reentrenamiento, las métricas de impacto y costo de gestión o el monitoreo de estos modelos.
---

# Modelos de cobranzas

Cobranzas usa las mismas reglas que los scores de riesgo (`credit-scoring/`: target, particiones, leakage, features, ratings, monitoreo) más las específicas de este dominio, porque **la gestión cambia el resultado que se intenta predecir**.

## Flujo

| Etapa | Leer |
|---|---|
| Problem framing, acción por segmento, grupo de control, métricas, operación | `references/00-flujo.md` |
| Universo, target de pase de tramo o autocura, features y leakage propios | `references/01-target-y-features.md` |
| Chequeos | `references/02-chequeos.md` |
| Reglas generales de scoring | `credit-scoring/00-flujo.md` y el archivo de cada etapa |
| Grupo de control e impacto | `credit-scoring/11-experimentacion.md` |
| Ratings | `credit-scoring/10-ratings.md` |
| Monitoreo y regla de promoción | `credit-scoring/07-estabilidad-monitoreo.md` |

Empezar completando `templates/problem-framing.md` con cobranzas.

## Reglas que no se negocian

1. **El modelo se entrena y se evalúa solo con el grupo de control.** Las cuentas gestionadas según el modelo reflejan la gestión, no el riesgo original.
2. El grupo de control es aleatorio, escalonado por rating, persistente entre corridas y lo bastante grande para reentrenar, no solo para medir.
3. La autocura se mide solo donde no hubo gestión.
4. Gestiones, contactos y promesas del episodio actual son leakage. Solo valen las de episodios anteriores.
5. El modelo se compara siempre contra la segmentación o regla vigente de cobranzas.
6. Discriminación del modelo (AUC/KS sobre control) e impacto de la gestión (tratamiento vs. control, con intención de tratamiento) son métricas distintas y se reportan por separado.
7. El reentrenamiento mensual pasa por la regla champion / challenger / recalibrado.
8. Las ventanas de espera por segmento salen de las curvas de pago por rating y de la capacidad operativa.

## Chequeos

`scripts/check_universe.py`, `scripts/check_leakage.py` (con gestiones del episodio actual en `forbidden_columns.txt`), `scripts/check_concentration.py` y `scripts/psi.py`. Ver `references/02-chequeos.md`.
