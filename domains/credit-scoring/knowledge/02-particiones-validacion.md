# Particiones y validación

En riesgo de crédito el modelo se usa en el futuro, sobre poblaciones que todavía no existen. La validación tiene que imitar eso.

## Regla principal

**La validación final es out-of-time (OOT).** Un split aleatorio mezcla meses y sobreestima el desempeño, porque el modelo ve condiciones económicas, políticas y campañas del mismo período que evalúa.

## Esquema recomendado

```
|---- desarrollo (train + test aleatorio) ----|-- gap --|---- OOT ----|
   originaciones ene-2023 a dic-2024              ene-mar    abr-jun 2025
```

- **Desarrollo:** se divide en train y test aleatorio (o por grupos) solo para elegir hiperparámetros.
- **Gap (opcional):** meses que se dejan afuera para que el OOT no comparta condiciones con el final del desarrollo.
- **OOT:** la evaluación honesta. Se mira una sola vez, al final. Si se usa para iterar, deja de ser OOT.
- Si hay suficientes datos, sumar un **backtest** con varias ventanas OOT sucesivas para ver la variabilidad de las métricas.

## Detalles que rompen la validación

- **Misma persona en dos particiones.** Si una persona tiene varias solicitudes, todas van a la misma partición (split por grupo).
- **Transformaciones ajustadas con toda la muestra.** Binning, WoE, imputación, escalado y selección de variables se ajustan solo con train y se aplican al resto.
- **Selección de variables mirando el OOT.** Cualquier decisión tomada mirando el OOT lo contamina.
- **Cohortes inmaduras en el OOT** (ver `01-definicion-default.md`).
- **Validación cruzada con k-fold aleatorio** sobre datos temporales: sirve para tunear, nunca como métrica final.

## Qué reportar

- Métricas en train, test y OOT lado a lado. Una caída grande de test a OOT es una señal, no un detalle.
- Intervalos de confianza (bootstrap) de AUC/Gini y KS en el OOT.
- Métricas por cohorte mensual del OOT, no solo el agregado.
- Métricas por segmento relevante (producto, canal, región, cliente nuevo vs. existente).
