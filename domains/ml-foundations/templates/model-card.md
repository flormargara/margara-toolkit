# Ficha del modelo — [nombre] v[versión]

<!-- doc-anchor: repo=<repo> rama=<rama> commit=<sha corto> revisado=<AAAA-MM-DD> -->

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
- Demora entre la predicción y la acción:
- Población excluida (con volumen):
- Uso permitido:
- Usos no permitidos:

### Consumo y respaldo
- Quién consume la salida y qué sistema o proceso la toma:
- Modo de entrega (batch, API, tabla, archivo), frecuencia y SLA:
- Medio de envío y qué pasa si falla (reintento, reenvío, aviso):
- Si el modelo falla o no está disponible: respaldo (regla, versión anterior, no decidir) y si el sistema falla abierto o cerrado:
- Responsable de mantenimiento por tramo (datos, pipeline, integración, monitoreo):
- En tiempo real: latencia p50 y p99, throughput, disponibilidad, frescura de las features online:

## 2. Target
- Evento o valor que se predice:
- Grano:
- Horizonte (y cómo se garantiza la madurez):
- Tipo (binario / continuo / conteo):

## 3. Datos y particiones

| Partición | Período | N | Eventos / media del target | Uso |
|---|---|---|---|---|
| Train | | | | Entrenamiento |
| Test | | | | Selección (early stopping, trials, variables, calibración) o evaluación |
| Validación final | | | | Árbitro |

Perfil del target por período y veredicto de `target_profile.py`:

Esquema de validación (árbitro, vista del árbitro —completa o sin entidades vistas— y búsqueda dentro de train):

Veredicto de `check_universe.py`:

Versión del dataset y veredicto de `check_dataset.py` (ver contrato del dataset):

Tablas de las que depende el modelo (para el gate de entradas):

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

Si el test se usó para elegir, su métrica es optimista: no leerla como desempeño.

| Métrica | Train | Test (selección / evaluación) | Validación final completa (IC 95%) | Validación final sin entidades vistas (IC 95%) |
|---|---|---|---|---|
| | | | | |
| PSI de la predicción vs. desarrollo | — | | | |

Leaderboard (enlace) y líder elegido:

Desempeño por período y por segmento:

## 7. Umbral de decisión
Tabla de opciones entregada y umbral elegido por:

## 8. Limitaciones y riesgos

## 9. Experimento, monitoreo y promoción

Grupo de control (proporción, persistencia, exclusiones, qué recibe):

Métrica de impacto y ficha de impacto (enlace):

Tabla de salida (nombre y columnas: identificador, fecha de predicción, modelo, versión, score, banda o decisión, variante de experimento, partición):

Calendario de pipelines (entrenamiento, inferencia, monitoreo) y demora del ground truth:

Referencia del monitoreo: métrica de la validación final de esta versión y artefactos del modelo vigente.

| Capa | Métrica | Frecuencia | Umbral de alerta | Responsable | Acción |
|---|---|---|---|---|---|
| Negocio | | | | | |
| Modelo | Métrica principal vs. validación final de la versión | Por cohorte madura | −10% alerta, −20% crítico, con IC que excluya la referencia | | |
| Modelo | PSI de la predicción | | > 0.25 | | |
| Datos | Gate de entradas: esquema, volumen, frescura | Cada corrida | Falla cerrada | | |

Regla de promoción (margen mínimo para reemplazar al vigente):

## 10. Historial de cambios

| Versión | Fecha | Cambio | Motivo | Aprobado por |
|---|---|---|---|---|
| | | | | |
