# Experimentación en crédito

Aplica todo `ml-foundations/knowledge/07-experimentacion.md`: grupo de control por banda, tamaño mínimo, control persistente, ITT y separación entre discriminación e impacto. Acá están los experimentos propios de crédito.

## Bandas de prueba en originación

Para saber cómo pagan los solicitantes que hoy se rechazan, aprobar una muestra aleatoria y acotada **por debajo del corte vigente**:

- Definir el tamaño por la cantidad de malos que hace falta observar y el monto máximo de pérdida que el negocio acepta.
- Limitar el monto y el plazo de esas operaciones.
- Es la única evidencia directa para reject inference y para mover el corte (ver `06-sesgo-seleccion.md`).

## Estrategias de límite

Para scores comportamentales, upsell y downsell:

- Probar dos o tres estrategias (por ejemplo, distintos porcentajes de aumento) contra un grupo control sin cambio, dentro de cada rating.
- Medir uso, ingresos por intereses, mora y pérdida en una ventana suficiente; un aumento de límite puede subir el uso rápido y la mora más tarde.
- Definir de antemano qué cuentas son elegibles (por ejemplo, activas, con buen comportamiento de pago en los últimos meses y sin bloqueos recientes).

## Cambios de política

Cada cambio de regla o de corte se identifica con una versión de política o un ID de campaña registrado en la evaluación (ver `12-trazabilidad.md`), para poder comparar resultados entre versiones.
