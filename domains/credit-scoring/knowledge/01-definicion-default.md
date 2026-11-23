# Definición del target (default)

El target es la decisión metodológica más importante del score. Un buen modelo sobre un target mal definido optimiza otra cosa.

## Componentes que hay que fijar por escrito

1. **Evento de default.** Por ejemplo: 90+ días de atraso, pase a castigo, refinanciación por dificultad, quiebra. Usar la definición regulatoria o la interna de riesgo; no inventar una propia sin acordarla.
2. **Ventana de desempeño.** Período después del punto de decisión en el que se observa si ocurre el evento. Típico: 12 meses para consumo, 6 para microcrédito, 18 a 24 para hipotecario. Justificarla con curvas de maduración (vintage): elegir el punto en que la tasa acumulada de malos se estabiliza.
3. **Regla de "peor estado".** Si en la ventana el cliente llegó a 90+ aunque después se normalizó, ¿es malo? Lo habitual es usar el peor estado alcanzado.
4. **Indeterminados.** Casos entre bueno y malo (por ejemplo 30-89 días). Opciones: excluirlos del entrenamiento y reportar su volumen, o asignarlos con criterio documentado. Nunca descartarlos en silencio.
5. **Exclusiones.** Fraude, fallecidos, cuentas canceladas anticipadamente, préstamos de empleados, operaciones de prueba. Documentar cada exclusión con su volumen.
6. **Unidad de análisis.** Persona, préstamo o solicitud. Si una persona tiene varios préstamos, definir cómo se agregan para no contar dos veces ni filtrar información entre particiones.

## Chequeos obligatorios

- Tasa de malos por cohorte de originación: si cambia mucho entre cohortes, entenderlo antes de seguir (cambio de política, de producto, de ciclo económico).
- Cohortes inmaduras: no incluir originaciones cuya ventana de desempeño todavía no terminó. Es un error frecuente que subestima la tasa de malos de los meses recientes.
- Cantidad absoluta de malos: con menos de unos pocos cientos de eventos, preferir modelos más simples y menos variables.
- Comparar la definición elegida contra una alternativa (por ejemplo 60+ vs 90+) y reportar cuánto cambia la población de malos.

## Errores típicos

- Definir el default con un campo de estado actual en lugar de reconstruir la historia de atrasos a la fecha correcta.
- Usar ventanas distintas para distintas cohortes sin darse cuenta.
- Mezclar productos con dinámicas de pago distintas bajo un mismo target.
