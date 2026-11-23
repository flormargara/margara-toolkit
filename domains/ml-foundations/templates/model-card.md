# Ficha del modelo — [nombre] v[versión]

| Campo | Valor |
|---|---|
| Dueño | |
| Desarrollado por | |
| Fecha | |
| Estado | Desarrollo / Validación / Producción / Retirado |
| Versión de datos | |
| Repositorio, commit y tag de imagen | |
| Próxima revisión | |

## 1. Propósito y uso
- Decisión que apoya:
- Población objetivo:
- Momento de la predicción:
- Población excluida (con volumen):
- Uso permitido:
- Usos no permitidos:

## 2. Target
- Evento o valor que se predice:
- Grano:
- Horizonte (y cómo se garantiza la madurez):
- Tipo (binario / continuo / conteo):

## 3. Datos y particiones

| Partición | Período | N | Eventos / media del target |
|---|---|---|---|
| Train | | | |
| Test | | | |
| Validación final | | | |

Esquema de validación (árbitro y búsqueda dentro de train):

Veredicto de `check_universe.py`:

Fuentes de datos y cobertura de trazabilidad:

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

| Variable | Descripción | Fuente | Disponible al predecir | Dirección esperada | Participación en la importancia |
|---|---|---|---|---|---|
| | | | | | |

Concentración de importancia (top-1, top-3, número efectivo):

## 5. Modelo
- Métrica principal y criterio de "suficientemente bueno":
- Baselines (ingenuo, regla, sin tunear) y comparación:
- Tipo de modelo y motivo:
- Experimentos relevantes (ver registro de experimentos):
- Rebalanceo y recalibración:
- Calibración:

## 6. Desempeño

| Métrica | Train | Test | Validación final (IC 95%) |
|---|---|---|---|
| | | | |
| PSI de la predicción vs. desarrollo | — | | |

Desempeño por período y por segmento:

## 7. Umbral de decisión
Tabla de opciones entregada y umbral elegido por:

## 8. Limitaciones y riesgos

## 9. Experimento, monitoreo y promoción

Grupo de control (proporción, persistencia, exclusiones, qué recibe):

Métrica de impacto:

| Capa | Métrica | Frecuencia | Umbral de alerta | Responsable | Acción |
|---|---|---|---|---|---|
| Negocio | | | | | |
| Modelo | PSI de la predicción | | > 0.25 | | |
| Datos | Frescura de particiones | Cada corrida | | | |

Regla de promoción (margen mínimo para reemplazar al vigente):

## 10. Historial de cambios

| Versión | Fecha | Cambio | Motivo | Aprobado por |
|---|---|---|---|---|
| | | | | |
