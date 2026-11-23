# Instrucciones para agentes

Punto de entrada común para cualquier herramienta o modelo. Copiar como `AGENTS.md` en la raíz de un proyecto, dejando solo las secciones de los dominios que el proyecto usa.

El contenido completo vive en `~/projects/margara-toolkit/domains/`. Leer el archivo de la etapa en curso; no cargar todo de entrada.

## Credit scoring

Cuando el trabajo implique construir, modificar o validar un score de riesgo crediticio:

1. Seguir el flujo de `domains/credit-scoring/knowledge/00-flujo.md` y leer el archivo de cada etapa al empezarla.
2. Respetar siempre:
   - Validación final out-of-time.
   - Ninguna variable posterior al punto de decisión.
   - Transformaciones ajustadas solo con train.
   - La misma persona nunca en dos particiones.
   - Baseline de regresión logística.
   - AUC > 0.90 o IV > 0.5: revisar leakage antes de seguir.
3. Antes de reportar métricas de un modelo nuevo, correr:
   `python3 ~/projects/margara-toolkit/domains/credit-scoring/checks/check_leakage.py --features <lista_features.txt>`
4. Al cerrar el modelo, completar las plantillas de `domains/credit-scoring/templates/` dentro del proyecto.
5. Si una regla choca con lo pedido, decirlo explícitamente.
