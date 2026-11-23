# Leaderboard — [proyecto]

Versión del dataset: [versión] · Métrica principal: [métrica, dirección] · Árbitro: [validación final, vista completa o sin entidades vistas]

Nunca se borra una fila. Una versión nueva del dataset abre una sección nueva y vuelve a correr los baselines.

| # | Carpeta | Idea | Basado en | Métrica principal: búsqueda (media ± dispersión) / árbitro | Secundarias | Veredicto |
|---|---|---|---|---|---|---|
| 00 | `experiments/00_baseline/` | Ingenuo (…) + regla (…) + modelo sin tunear (…) | — | | | ✅ piso de comparación |
| 01 | `experiments/01_<nombre>/` | <idea en una oración> | 00 | | | |

Veredictos: ✅ nuevo líder · ✅ válido sin mejora · ❌ descartado · ⚠️ requiere revisión.

## Líder vigente

Experimento `NN`: <por qué gana en la métrica principal, y si la diferencia supera la dispersión>.

## Próximos experimentos sugeridos

- <idea concreta, con el motivo>

## Registro de cada experimento (`RESULT.md` en su carpeta)

1. Hipótesis.
2. Base y cambio exacto respecto de ella.
3. Métricas: búsqueda (media y dispersión) y árbitro (una vez), con el tamaño de cada conjunto.
4. Señales revisadas (leakage, sobreajuste, inestabilidad, desbalance, error por segmento).
5. Veredicto.
