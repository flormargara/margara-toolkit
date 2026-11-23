# Definición del target (default)

El target es la decisión metodológica más importante del score. Un buen modelo sobre un target mal definido optimiza otra cosa.

## Componentes que hay que fijar por escrito

1. **Evento de default.** Por ejemplo: 90+ días de atraso, pase a castigo, refinanciación por dificultad, quiebra. Partir de la definición regulatoria vigente (categorías de previsión por días de atraso) o de la interna de riesgo; no inventar una propia sin acordarla. Justificar el tramo elegido con un análisis de roll rate (abajo).
2. **Ventana de desempeño.** Período después del punto de decisión en el que se observa si ocurre el evento. Típico: 12 meses para consumo, 6 para microcrédito, 18 a 24 para hipotecario. Justificarla con curvas de maduración (vintage): elegir el punto en que la tasa acumulada de malos se estabiliza. Los targets tempranos (por ejemplo 30+ en los 90 días posteriores al primer vencimiento) dan feedback rápido, pero hay que mostrar que ordenan igual que un target de ventana completa.
3. **Regla de "peor estado".** Si en la ventana el cliente llegó a 90+ aunque después se normalizó, ¿es malo? Lo habitual es usar el peor estado alcanzado.
4. **Indeterminados.** Casos entre bueno y malo (por ejemplo 30-89 días). Opciones: excluirlos del entrenamiento y reportar su volumen, o asignarlos con criterio documentado. Nunca descartarlos en silencio.
5. **Refinanciaciones, reestructuraciones y renovaciones (3R).** Una refinanciación o reestructuración por dificultad de pago cuenta como evento aunque el atraso se haya regularizado. Una renovación sin atraso relevante no es necesariamente un mal pagador. Documentar cómo se trata cada una.
6. **Monto mínimo.** Saldos vencidos muy chicos (comisiones, diferencias de redondeo) generan malos ruidosos. Fijar un umbral de monto que se considere pequeño en el contexto del mercado y verificar que los casos excluidos por ese umbral no superen el 15-20% de los malos.
7. **Exclusiones.** Fraude, fallecidos, cuentas canceladas anticipadamente, préstamos de empleados, operaciones de prueba, casos aceptados o rechazados automáticamente por política. Documentar cada exclusión con su volumen.
8. **Unidad de análisis.** Persona, préstamo, cuenta o solicitud. Si una persona tiene varios préstamos, definir cómo se agregan para no contar dos veces ni filtrar información entre particiones.

## Análisis de roll rate

Sirve para elegir qué tramo de atraso es "malo" con evidencia, en lugar de por costumbre. Se usa porque las pérdidas reales (castigos) suelen ser muy pocas para entrenar, y hace falta un tramo de atraso que tenga alta probabilidad de terminar en pérdida.

**Enfoque 1 — peor tramo y resultado posterior.** Agrupar las cuentas por su peor tramo de atraso en X meses y medir qué proporción cae en default en los Y meses siguientes.

- Un tramo con probabilidad de llegar a default mayor a 25-30% se considera **malo**.
- Un tramo con tasa de default menor al promedio de la cartera se considera **bueno**.
- El resto es **indeterminado**.

**Enfoque 2 — matriz de transición.** Tramo en el período t contra tramo en t+1. Elegir como "malo" el primer tramo en el que es más probable empeorar (roll forward) que quedarse o curarse.

Reportar la matriz usada y la decisión tomada en la ficha del modelo.

## Chequeos obligatorios

- Tasa de malos por cohorte de originación: si cambia mucho entre cohortes, entenderlo antes de seguir (cambio de política, de producto, de ciclo económico).
- **Madurez impuesta en la query, no a mano.** La ventana de datos del universo tiene que terminar antes de `hoy − horizonte`, de modo que ninguna cohorte inmadura pueda entrar aunque alguien cambie la fecha de corrida. Las cohortes inmaduras subestiman la tasa de malos de los meses recientes.
- Cantidad absoluta de malos: con menos de unos pocos cientos de eventos, preferir modelos más simples y menos variables.
- Comparar la definición elegida contra una alternativa (por ejemplo 60+ vs 90+) y reportar cuánto cambia la población de malos.
- El target se elige por la decisión que apoya, no porque sea el que mejor se predice. Entre opciones igualmente útiles, recién ahí la predictibilidad desempata.

## Errores típicos

- Definir el default con un campo de estado actual en lugar de reconstruir la historia de atrasos a la fecha correcta.
- Usar ventanas distintas para distintas cohortes sin darse cuenta.
- Mezclar productos con dinámicas de pago distintas bajo un mismo target.
- Elegir el target "más predecible" en lugar del que responde a la decisión de negocio.
