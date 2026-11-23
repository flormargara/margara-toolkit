---
name: collections-ml
description: Metodología para modelos de cobranzas y mora (segmentación de mora temprana, pase de tramo, autocura, priorización de gestión). Usar al definir el problem framing de un modelo de cobranzas, el universo por fecha de entrada en mora, el target de pase de tramo o autocura, las ventanas de espera y acciones por segmento, el grupo de control, el reentrenamiento, las métricas de impacto y costo de gestión o el monitoreo de estos modelos. Incluye las prácticas generales de ML y las de crédito.
---

# Modelos de cobranzas

Cobranzas usa tres capas de conocimiento: las prácticas generales de ML (`ml-foundations/`), las de crédito (`credit-scoring/`) y las específicas de este dominio (`references/`), porque **la gestión cambia el resultado que se intenta predecir**.

## Flujo

| Etapa | Leer |
|---|---|
| Problem framing, acción por segmento, grupo de control, métricas, operación | `references/00-flujo.md` |
| Universo, target de pase de tramo o autocura, features y leakage propios | `references/01-target-y-features.md` |
| Chequeos | `references/02-chequeos.md` |
| Universo y particiones | `ml-foundations/knowledge/01-universo-particiones.md` |
| Leakage, features, modelado | `ml-foundations/knowledge/02-leakage.md`, `03-features.md`, `04-modelado.md` |
| Grupo de control e impacto | `ml-foundations/knowledge/07-experimentacion.md` |
| Monitoreo y regla de promoción | `ml-foundations/knowledge/06-monitoreo.md` |
| Definición de tramos de mora | `credit-scoring/knowledge/01-definicion-default.md` |
| Ratings | `credit-scoring/knowledge/10-ratings.md` |

Empezar completando `templates/problem-framing.md` con cobranzas.

## Reglas que no se negocian

Todas las de la skill `ml-practices`, y además:

1. **El modelo se entrena y se evalúa solo con el grupo de control.** Las cuentas gestionadas según el modelo reflejan la gestión, no el riesgo original.
2. El grupo de control es aleatorio, escalonado por rating, persistente entre corridas y lo bastante grande para reentrenar, no solo para medir.
3. La autocura se mide solo donde no hubo gestión.
4. Gestiones, contactos y promesas del episodio actual son leakage. Solo valen las de episodios anteriores.
5. El modelo se compara siempre contra la segmentación o regla vigente de cobranzas.
6. Discriminación del modelo (sobre control) e impacto de la gestión (tratamiento vs. control, con intención de tratamiento) son métricas distintas y se reportan por separado.
7. El reentrenamiento mensual pasa por la regla champion / challenger / recalibrado.
8. Las ventanas de espera por segmento salen de las curvas de pago por rating y de la capacidad operativa.

## Chequeos

Propios de cobranzas, en `checks/`:

| Chequeo | Uso |
|---|---|
| Entrenamiento solo con control | `python3 checks/check_training_population.py universo.csv --model-start AAAA-MM-DD` (con `--target-kind autocura` si el target es autocura) |
| Grupo de control | `python3 checks/check_control_group.py asignaciones.csv --expected A=0.03,B=0.05,C=0.08 --target-col <target> --min-control-events <n>`: persistencia, proporción por rating y tamaño para reentrenar |
| Ratings sobre control | `python3 credit-scoring/checks/check_ratings.py control.csv --order ... --expected ... --where grupo=control` |

Además, los genéricos de `ml-foundations/checks/` (`check_universe.py`, `check_dataset.py`, `check_leakage.py`, `check_concentration.py`, `psi.py`), con la lista de patrones de `credit-scoring/checks/forbidden_columns.example.txt`. Ver `references/02-chequeos.md`.
