# Ficha de impacto — [modelo] en [implementación]

Ver `ml-foundations/knowledge/07-experimentacion.md`. Una ficha por implementación (dónde y cómo se usa el modelo); en soluciones con varios modelos, una sub-ficha por modelo u objetivo.

| Campo | Valor |
|---|---|
| Modelo y versiones cubiertas | |
| Implementación (área, flujo, decisión) | |
| Dueño del dominio (aprueba) | |
| Responsable del cálculo | |
| Estado | borrador / propuesta / aprobada / pausada / retirada |

## 1. Objetivo

- Objetivo de negocio:
- KPI (nombre nativo del dominio):
- Unidad:
- Dirección deseada: sube / baja
- Meta y horizonte (si existen):

## 2. Cálculos candidatos

| Candidato | Tablas | Supuestos | Contrafactual | Valor de muestra |
|---|---|---|---|---|
| A | | | | |

## 3. Elección

- Cálculo elegido:
- Tipo de contrafactual: control/holdout / A/B / champion-challenger / línea base / sin contrafactual
- Definición del contrafactual:
- Ventana de maduración (períodos hasta que el resultado es definitivo):

## 4. Cálculo versionado

| Versión | Archivo | Commit | Parámetros | Fecha |
|---|---|---|---|---|
| v1 | | | | |

Contrato de salida por período: `valor_observado`, `valor_contrafactual` (vacío si no hay), `impacto`, `n`, `intervalo` (opcional), `advertencias`.

## 5. Aprobación

| Versión | Aprobó | Fecha | Evidencia |
|---|---|---|---|
| | | | |

## Registro de mediciones

Append-only. Un recálculo agrega una fila; nunca se edita una anterior.

| Período | Revisión | Estado (preliminar / definitivo / sin dato) | Observado | Contrafactual | Impacto | n | Intervalo | Versión del modelo | Versión del cálculo | Oficial (sí / ensayo) |
|---|---|---|---|---|---|---|---|---|---|---|
| | | | | | | | | | | |

## Pendientes

- [ ] (por ejemplo: diseñar holdout, conseguir dato faltante, aprobar versión nueva)
