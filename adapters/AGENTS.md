# Instrucciones para agentes

Punto de entrada común para cualquier herramienta o modelo. Copiar como `AGENTS.md` en la raíz de un proyecto, dejando solo las secciones de los dominios que el proyecto usa.

El contenido completo vive en `~/projects/margara-toolkit/`. Leer el archivo de la etapa en curso; no cargar todo de entrada.

## Forma de trabajo

Seguir `shared/knowledge/agent-workflow.md`: archivos de memoria del proyecto (`DISCOVERY_LOG`, `UNIVERSE_LOG`, `FEATURE_CATALOG`, `MODELING_SPEC`, `EXPERIMENTS_LOG`), criterio de cierre con veredicto en cada paso, definiciones de negocio preguntadas de a una, y el código manda sobre la documentación.

## Credit scoring

Cuando el trabajo implique construir, modificar, validar o monitorear un score de riesgo crediticio:

1. Seguir el flujo de `domains/credit-scoring/knowledge/00-flujo.md` y leer el archivo de cada etapa al empezarla.
2. Respetar siempre:
   - Validación final out-of-time; elegibilidad idéntica en train, validación y scoring.
   - Ninguna variable posterior al punto de decisión.
   - Transformaciones y sampling ajustados solo con train.
   - La misma persona nunca en dos particiones.
   - El conjunto del veredicto se mira una vez; la búsqueda vive dentro de train.
   - Baselines y experimentos de un solo cambio.
   - AUC > 0.90, IV > 0.5 o una variable dominante: revisar leakage antes de seguir.
   - Reemplazar el modelo vigente solo por un margen mínimo y sin empeorar la calibración por rating.
3. Antes de reportar métricas de un modelo nuevo, correr en `domains/credit-scoring/checks/`:
   `check_universe.py`, `check_leakage.py --features <lista>` y `check_concentration.py`.
4. Al cerrar el modelo, completar las plantillas de `domains/credit-scoring/templates/` dentro del proyecto.
5. Si una regla choca con lo pedido, decirlo explícitamente.

## Cobranzas

Además de lo anterior, seguir `domains/collections/knowledge/`:

- El modelo se entrena y evalúa solo con el grupo de control.
- Gestiones, contactos y promesas del episodio actual de mora son leakage.
- Discriminación (sobre control) e impacto (tratamiento vs. control) se reportan por separado.
- Empezar por `domains/collections/templates/problem-framing.md`.
