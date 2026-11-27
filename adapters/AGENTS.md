# Instrucciones para agentes

Punto de entrada común para cualquier herramienta o modelo. Copiar como `AGENTS.md` en la raíz de un proyecto, dejando solo las secciones de los dominios que el proyecto usa.

El contenido completo vive en `~/projects/margara-toolkit/`. Leer el archivo de la etapa en curso; no cargar todo de entrada.

## Forma de trabajo

Seguir `shared/knowledge/agent-workflow.md`: archivos de memoria del proyecto (`DISCOVERY_LOG`, `UNIVERSE_LOG`, `FEATURE_CATALOG`, `MODELING_SPEC`, `EXPERIMENTS_LOG`), criterio de cierre con veredicto en cada paso, definiciones de negocio preguntadas de a una, y el código manda sobre la documentación.

## ML supervisado (cualquier proyecto de modelado)

1. Seguir el flujo de `domains/ml-foundations/knowledge/00-flujo.md` y leer el archivo de cada etapa al empezarla.
2. Respetar siempre:
   - Validación final fuera de tiempo; elegibilidad idéntica en train, validación y predicción.
   - Ninguna variable posterior al momento de la predicción.
   - Transformaciones y sampling ajustados solo con train.
   - La misma entidad nunca en dos particiones de la búsqueda; la validación final se reporta completa y sin entidades vistas.
   - Si la acción llega después de la predicción, el target se mide desde que se puede actuar.
   - El conjunto del veredicto se mira una vez; la búsqueda y la selección de variables con target viven dentro de train.
   - Train, validación y scoring salen de la misma receta con distinto universo.
   - Baselines y experimentos de un solo cambio, en un leaderboard; métricas con su dispersión.
   - Desempeño sospechosamente alto o una variable dominante: revisar leakage antes de seguir.
   - Reemplazar el modelo vigente solo por un margen mínimo y sin empeorar la calibración.
   - Si la acción cambia el resultado, entrenar y evaluar con el grupo de control.
3. Correr en `domains/ml-foundations/checks/`: `target_profile.py` antes de particionar; y antes de reportar métricas de un modelo nuevo,
   `check_universe.py`, `check_leakage.py --features <lista>`, `check_dataset.py` y `check_concentration.py`.
   Al cerrar la lista de features, `check_feature_names.py`; en monitoreo, `psi.py`; y antes de reemplazar el modelo vigente, `promotion.py`.
4. Al cerrar el modelo, completar las plantillas de `domains/ml-foundations/templates/` dentro del proyecto.
5. Si una regla choca con lo pedido, decirlo explícitamente.

## Con ai-mllc

Si el proyecto usa ai-mllc, generar su catálogo de golden rules desde el toolkit con `adapters/mllc/compose.py` (ver `adapters/mllc/README.md`).

## Credit scoring

Además de lo anterior, seguir `domains/credit-scoring/knowledge/00-flujo.md`, que indica para cada etapa el archivo general y el de crédito:

- Default definido con roll rate y acordado con riesgo; ninguna cohorte sin ventana de desempeño completa.
- AUC > 0.90 o IV > 0.5: revisar leakage.
- Baselines de regresión logística sobre WoE y de la política vigente.
- Score registrado para todos los solicitantes, incluidos los rechazados por reglas.
- Ratings validados con error de calibración acotado; el corte lo decide el dueño del riesgo.
- Chequeos de crédito en `domains/credit-scoring/checks/`: `roll_rate.py --bad-from <tramo>` al definir el default, `check_woe_bins.py` sobre la tabla de binning y `check_ratings.py` sobre la muestra donde se verifican los cortes.
- Lista de leakage de crédito: `domains/credit-scoring/checks/forbidden_columns.example.txt`.
- Plantillas de crédito: `domains/credit-scoring/templates/`.

## Cobranzas

Además de ML y crédito, seguir `domains/collections/knowledge/`:

- El modelo se entrena y evalúa solo con el grupo de control: `domains/collections/checks/check_training_population.py` en verde, y `check_control_group.py` sobre el registro de asignaciones.
- Gestiones, contactos y promesas del episodio actual de mora son leakage.
- Discriminación (sobre control) e impacto (tratamiento vs. control) se reportan por separado.
- Empezar por `domains/collections/templates/problem-framing.md`.
