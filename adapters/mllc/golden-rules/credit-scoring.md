# Golden rules de credit-scoring

Catálogo de reglas de `domains/credit-scoring` en el formato de golden rules de ai-mllc. Se compone después de `ml-foundations`, que ya tiene las reglas generales: `compose.py ml-foundations credit-scoring`. Acá solo va lo propio de crédito. Cada regla remite al archivo del toolkit que la explica. Los chequeos viven en `~/projects/margara-toolkit/domains/credit-scoring/checks/`; el código de salida 0 es `cumple`, 1 es `no_cumple`, y si no se pudo correr por falta de insumos es `evidencia_insuficiente`.

## cr-decision-y-poblacion (v1)

- fuerza: alerta
- etapa: intake
- mecanismo: discusion
- estado: active

Discutir con el Data Scientist y registrar en el frame: qué decisión toma el score (aprobar, asignar línea, fijar tasa, mover un límite), sobre qué población, en qué momento exacto se calcula, qué hace hoy la política de riesgo sin el modelo, qué cuesta cada tipo de error y a quién no se va a scorear (criterio de scoreabilidad y exclusiones por política). Ver `domains/credit-scoring/knowledge/00-flujo.md`, "Etapa 1".

## cr-trazabilidad-de-la-cadena (v1)

- fuerza: bloqueante
- etapa: understand
- mecanismo: atestacion
- estado: active

Antes de armar el universo, presentar la cobertura de cada salto de la cadena solicitud → consulta a burós → oferta → aceptación → desembolso → desempeño para el período candidato: qué porcentaje de registros se une con el salto siguiente y con qué clave. Si una parte relevante se pierde, decir cuánto se achica el universo usable y si queda sesgado (por ejemplo, solo algunos canales). Ver `12-trazabilidad.md`.

## cr-default-con-roll-rate (v1)

- fuerza: bloqueante
- etapa: observe
- mecanismo: check_determinista
- estado: active

Correr `python3 roll_rate.py <historia_mensual.csv> --id-col <cuenta> --period-col <mes> --dpd-col <dias_atraso> --obs-months <meses_observacion> --perf-months <ventana_desempeño> --bad-from <tramo_propuesto>` sobre la historia de atrasos reconstruida a cada fecha. FAIL (el tramo propuesto o uno peor sale "bueno") es `no_cumple`. Presentar la matriz y las advertencias. Ver `01-definicion-default.md`, "Análisis de roll rate".

## cr-componentes-del-target (v1)

- fuerza: bloqueante
- etapa: observe
- mecanismo: atestacion
- estado: active

El target queda escrito con sus ocho componentes: evento de default, ventana de desempeño justificada con curvas de maduración, regla de peor estado, indeterminados (con su volumen), tratamiento de refinanciaciones, reestructuraciones y renovaciones, monto mínimo (los malos excluidos por el umbral no superan el 15-20%), exclusiones (cada una con su volumen) y unidad de análisis. La ventana de desempeño es el `--horizon-days` de `ml-integridad-temporal`. Ver `01-definicion-default.md`.

## cr-tasa-de-malos-por-cohorte (v1)

- fuerza: alerta
- etapa: observe
- mecanismo: atestacion
- estado: active

Presentar la tasa y la cantidad de malos por cohorte de originación y por partición. Un cambio grande entre cohortes se explica antes de seguir (política, producto, ciclo). Con menos de unos pocos cientos de malos, proponer modelos simples y pocas variables. Si hubo un cambio de política en el período, el OOT queda después del cambio. Ver `01-definicion-default.md` y `02-particiones-validacion.md`.

## cr-leakage-de-credito (v1)

- fuerza: bloqueante
- etapa: features
- mecanismo: atestacion
- estado: active

El `forbidden_columns.txt` del proyecto incluye los patrones de `credit-scoring/checks/forbidden_columns.example.txt` adaptados a los nombres reales, y `ml-sin-columnas-prohibidas` corre con ese archivo. Atestar además que no entran el desempeño del propio préstamo, datos de buró consultados después de la evaluación ni variables de proceso (fecha o monto de desembolso, oferta final, analista). Ver `03-leakage.md`.

## cr-variables-sensibles (v1)

- fuerza: bloqueante
- etapa: features
- mecanismo: atestacion
- estado: active

Ninguna variable sensible o prohibida por la normativa local entra como feature (según el país: género, origen étnico, nacionalidad, religión, estado civil, discapacidad, entre otras; la lista vigente va en la constitución local). Atestar también la revisión de proxies: geografía fina, nombre, dispositivo, horario de solicitud. Ver `08-equidad-regulacion.md`.

## cr-binning-woe (v1)

- fuerza: bloqueante
- etapa: model
- mecanismo: check_determinista
- estado: active

El binning WoE mira el target: se ajusta solo con train, con buenos y malos, dentro del modelado. Correr `python3 check_woe_bins.py <binning_train.csv>` sobre la tabla de binning. Una variable no monótona o con IV alto solo pasa con `--allow-nonmonotonic` o `--allow-high-iv` y una justificación escrita. Ver `04-features.md`, "Binning y WoE".

## cr-baselines-de-credito (v1)

- fuerza: bloqueante
- etapa: model
- mecanismo: atestacion
- estado: active

Entre los baselines de `ml-baselines` están siempre una regresión logística sobre WoE y la política de riesgo vigente (sus reglas de buró, ingreso y endeudamiento). Presentar los dos en el leaderboard con Gini y KS. Ver `05-modelado-calibracion.md`, "Baseline de crédito".

## cr-alarma-de-desempeno (v1)

- fuerza: bloqueante
- etapa: model
- mecanismo: atestacion
- estado: active

Un AUC mayor a 0.90 en originación o una variable con IV mayor a 0.5 detiene el modelado hasta demostrar que no hay leakage: para cada variable sospechosa, de dónde sale y por qué estaría disponible en la fecha de la solicitud. Ver `03-leakage.md`, "Señales de alarma propias".

## cr-signos-coherentes (v1)

- fuerza: alerta
- etapa: model
- mecanismo: atestacion
- estado: active

En la regresión logística sobre WoE, los coeficientes tienen el signo que espera el negocio; un signo invertido se explica (colinealidad o datos) antes de aceptar el modelo. VIF menor a 2 como guía, con las excepciones justificadas. Ver `04-features.md`, "Regresión logística sobre WoE".

## cr-pd-calibrada (v1)

- fuerza: bloqueante
- etapa: model
- mecanismo: atestacion
- estado: active

Si la probabilidad de default se usa como número (pricing, provisiones, pérdida esperada), presentar su calibración por decil y por rating en el OOT: la tasa observada no se aleja más de ±5 puntos de la esperada (ajustado al tamaño de cada banda). Si no se usa como número, decirlo y la regla es `no_aplica`. Ver `05-modelado-calibracion.md`, "PD y calibración".

## cr-ratings-validados (v1)

- fuerza: bloqueante
- etapa: model
- mecanismo: check_determinista
- estado: active

Los cortes de rating se calculan en desarrollo y se verifican en el OOT: correr `python3 check_ratings.py <oot.csv> --order <A,B,C,...> --expected <A=...,B=...>` (con `--score-col` y `--cohort-col` si están). FAIL en monotonía, tamaño mínimo, calibración o cortes es `no_cumple`. Si el score no se lleva a ratings, la regla es `no_aplica`. Ver `10-ratings.md`.

## cr-metricas-por-cohorte-y-segmento (v1)

- fuerza: alerta
- etapa: model
- mecanismo: atestacion
- estado: active

Las métricas del OOT se presentan por cohorte de originación y por segmento (producto, canal, cliente nuevo o existente, con y sin historial en buró), no solo en el agregado. Ver `02-particiones-validacion.md`, "Qué reportar además de lo general".

## cr-sesgo-de-seleccion (v1)

- fuerza: alerta
- etapa: model
- mecanismo: discusion
- estado: active

Discutir con el Data Scientist el sesgo de entrenar con aprobados: la tasa de aprobación histórica, cómo cambió y qué se hace (técnica de reject inference con su supuesto, o limitar el uso del modelo a la zona aprobada). Si el objetivo es expandir la aprobación, proponer una banda de prueba. Registrar la decisión. Ver `06-sesgo-seleccion.md`.

## cr-auditoria-de-equidad (v1)

- fuerza: alerta
- etapa: model
- mecanismo: atestacion
- estado: active

Si hay una variable sensible disponible solo para auditar, presentar por grupo la tasa de aprobación al corte, la tasa de malos entre aprobados, el AUC y la calibración. Una diferencia grande se explica o se corrige. Si no hay variable para auditar, decirlo y la regla es `no_aplica`. Ver `08-equidad-regulacion.md`, "Métricas de auditoría".

## cr-punto-de-corte (v1)

- fuerza: bloqueante
- etapa: model
- mecanismo: discusion
- estado: active

El punto de corte lo decide el dueño del riesgo, no el agente ni el modelado. Presentar para cada corte posible la tasa de aprobación, la tasa de malos esperada en aprobados, el volumen y, si se tiene, la rentabilidad, y registrar quién eligió el corte y con qué criterio (mora máxima o aprobación objetivo). Ver `05-modelado-calibracion.md`, "Punto de corte".

## cr-registro-de-evaluaciones (v1)

- fuerza: alerta
- etapa: deploy
- mecanismo: discusion
- estado: active

Acordar qué registra cada evaluación en producción: identificadores de evaluación, persona y producto; score, rating y versión del modelo; versión de política o ID de campaña; resultado de cada regla; consultas a buró usadas. El score se calcula y registra para todos los solicitantes, incluidos los rechazados por reglas. Ver `12-trazabilidad.md` y `06-sesgo-seleccion.md`.

## cr-razones-de-rechazo (v1)

- fuerza: alerta
- etapa: deploy
- mecanismo: atestacion
- estado: active

El despliegue puede dar razones individuales de rechazo comprensibles para el solicitante: puntos por variable en la logística sobre WoE, o SHAP en un GBM, traducidos a lenguaje de negocio. Ver `08-equidad-regulacion.md`, "Explicabilidad de decisiones".

## cr-cortes-versionados (v1)

- fuerza: alerta
- etapa: deploy
- mecanismo: atestacion
- estado: active

Los cortes de rating se guardan como artefacto versionado junto con el modelo y se aplican de forma determinista. Si conviven modelos con letras, hay una tabla de equivalencias o nombres que dejen claro de qué modelo es cada rating. Ver `10-ratings.md`, "Aplicación en producción".
