# Ficha del modelo — [nombre] v[versión]

> Versión de crédito de la plantilla genérica de `ml-foundations/templates/`. Incluye todos sus puntos más los específicos de riesgo crediticio.

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

Cobertura de trazabilidad del período (evaluación → oferta → desembolso → desempeño):

Población de entrenamiento vs. de predicción (AUC adversarial y cómo se corrigió):

## 4. Variables

Embudo de selección:

| Paso | Variables que quedan |
|---|---|
| Candidatas | |
| Filtro manual de leakage | |
| Nulos / población mínima | |
| Varianza | |
| Estabilidad por período | |
| Correlación | |
| Selección multivariada | |
| Finales | |

| Variable | Descripción | Fuente | Disponible en decisión | Dirección del riesgo | IV | Participación en la importancia |
|---|---|---|---|---|---|---|
| | | | | | | |

Concentración de importancia (top-1, top-3, número efectivo):

Variables descartadas relevantes y motivo:

## 5. Modelo
- Métrica principal y criterio de "suficientemente bueno":
- Esquema de validación (árbitro y búsqueda dentro de train):
- Tipo y motivo de la elección:
- Baselines (ingenuo, regla, sin tunear) y comparación:
- Experimentos relevantes (ver EXPERIMENTS_LOG):
- Rebalanceo aplicado y recalibración:
- Calibración:
- Escalamiento a puntos (puntos base, odds base, PDO):

## 5b. Ratings

| Rating | Participación | Tasa esperada | Tasa observada (OOT) | Diferencia |
|---|---|---|---|---|
| | | | | |

Método de construcción de cortes y validación en segunda muestra:

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

## 10. Monitoreo, experimento y promoción

Grupo de control (proporción por rating, persistencia, exclusiones):

Métrica de impacto:

| Capa | Métrica | Frecuencia | Umbral de alerta | Responsable | Acción |
|---|---|---|---|---|---|
| Negocio | Tasa esperada vs. observada por rating | Mensual (cohortes maduras) | ± 5 pp | | |
| Modelo | PSI del score | Mensual | > 0.25 | | |
| Datos | Frescura de particiones de las fuentes | Cada corrida | | | |
| | | | | | |

Regla de promoción (margen mínimo para reemplazar al vigente):

## 11. Historial de cambios

| Versión | Fecha | Cambio | Motivo | Aprobado por |
|---|---|---|---|---|
| | | | | |
