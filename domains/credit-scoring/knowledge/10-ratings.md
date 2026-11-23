# Ratings

Un rating agrupa la población en bandas ordenadas de riesgo, identificadas por letras. En lugar de usar la probabilidad continua del modelo, se definen tramos de score y a cada tramo se le asigna una letra con una tasa de malos esperada. Es la forma habitual de llevar un score a políticas, límites y acciones de cobranza.

## Propiedades que debe tener una escala de ratings

1. **Monotonía:** la tasa de malos observada sube de forma estricta de la mejor a la peor letra.
2. **Tamaño mínimo por banda:** cada banda tiene al menos una fracción mínima de la población (por ejemplo 3%) y suficientes malos para que su tasa sea estable.
3. **Separación:** bandas contiguas tienen tasas claramente distintas; dos bandas con la misma tasa deberían unirse.
4. **Estabilidad:** la tasa de cada banda se mantiene entre cohortes.
5. **Utilidad:** las bandas se corresponden con acciones distintas. Si dos bandas llevan siempre a la misma acción, sobran.

## Construcción contra un perfil de tasas esperadas

1. Definir el **perfil de tasas esperadas** por banda. Puede venir de la política (por ejemplo tasas objetivo por rating ya usadas por riesgo) o generarse alrededor de la tasa de malos global con desplazamientos simétricos en escala logit.
2. Buscar los cortes de score que hacen que la tasa observada de cada banda quede lo más cerca posible de la esperada, respetando el tamaño mínimo. Una programación dinámica sobre la población ordenada por score resuelve esto de forma exacta; minimizar el **error máximo** entre bandas (norma infinito) evita que una banda quede muy desviada.
3. Dejar **bandas residuales** en los extremos para el remanente de población que no encaja en el perfil.
4. Probar varias cantidades de bandas y quedarse con la menor que cumple las propiedades.

## Validación de los cortes

- Calcular los cortes en una muestra (desarrollo) y **verificarlos en otra** (OOT): la tasa observada por banda en la segunda muestra no debe alejarse de la esperada más que el margen de aceptación (por ejemplo ±5 puntos).
- **Estresar los cortes**: repetir el cálculo con ruido en las tasas esperadas o con submuestras (Monte Carlo) y ver cuánto se mueven. Cortes muy sensibles indican bandas demasiado finas.
- Reportar por banda: cantidad, participación, malos, tasa observada, tasa esperada y diferencia.

## Aplicación en producción

- Los cortes se guardan como artefacto versionado junto con el modelo (`{rating: [límite inferior, límite superior]}`) y se aplican de forma determinista.
- Recalibrar los cortes es una alternativa a reentrenar cuando el orden se mantiene y cambió el nivel de riesgo (ver `07-estabilidad-monitoreo.md`).
- No mezclar convenciones de letras entre modelos que conviven sin una tabla de equivalencias: "B" tiene que significar lo mismo para quien toma la decisión, o el nombre tiene que dejar claro de qué modelo es.

## Monitoreo

- Distribución por rating en cada corrida (inmediato).
- Tasa esperada vs. observada por rating en cada cohorte madura (sobre el grupo de control si la acción cambia el resultado).
- Un desplazamiento de la población hacia ratings peores después de cambiar de modelo no prueba que el nuevo detecte mejor: confirmar con la tasa observada.
