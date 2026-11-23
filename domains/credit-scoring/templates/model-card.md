# Ficha del modelo — [nombre] v[versión]

| Campo | Valor |
|---|---|
| Dueño | |
| Desarrollado por | |
| Fecha | |
| Estado | Desarrollo / Validación / Producción / Retirado |
| Versión de datos | |
| Repositorio y commit | |
| Próxima revisión | |

## 1. Propósito y uso
- Decisión que toma:
- Población objetivo:
- Punto de decisión:
- Uso permitido:
- Usos no permitidos:

## 2. Target
- Evento de default:
- Ventana de desempeño (y justificación):
- Regla de peor estado:
- Indeterminados (tratamiento y volumen):
- Exclusiones (con volumen):

## 3. Datos y particiones

| Partición | Período de originación | N | Malos | Tasa de malos |
|---|---|---|---|---|
| Train | | | | |
| Test | | | | |
| OOT | | | | |

Fuentes de datos:

## 4. Variables

| Variable | Descripción | Fuente | Disponible en decisión | Dirección del riesgo | IV |
|---|---|---|---|---|---|
| | | | | | |

Variables descartadas relevantes y motivo:

## 5. Modelo
- Tipo y motivo de la elección:
- Baseline y comparación:
- Calibración:
- Escalamiento a puntos (puntos base, odds base, PDO):

## 6. Desempeño

| Métrica | Train | Test | OOT (IC 95%) |
|---|---|---|---|
| AUC | | | |
| Gini | | | |
| KS | | | |
| PSI del score vs. desarrollo | — | | |

Desempeño por segmento:

Calibración (PD estimada vs. observada por decil):

## 7. Punto de corte
Tabla de opciones entregada y corte elegido por:

## 8. Limitaciones y riesgos
- Sesgo de selección:
- Poblaciones no cubiertas:
- Variables con riesgo de discontinuidad:
- Otros:

## 9. Equidad
- Variables sensibles excluidas y proxies revisados:
- Métricas por grupo:
- Reason codes:

## 10. Monitoreo

| Métrica | Frecuencia | Umbral de alerta | Responsable | Acción |
|---|---|---|---|---|
| PSI del score | Mensual | > 0.25 | | |
| | | | | |

## 11. Historial de cambios

| Versión | Fecha | Cambio | Motivo | Aprobado por |
|---|---|---|---|---|
| | | | | |
