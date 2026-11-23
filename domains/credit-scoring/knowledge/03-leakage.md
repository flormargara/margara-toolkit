# Leakage en crédito

Aplica todo `ml-foundations/knowledge/02-leakage.md`. Acá están las fuentes de leakage propias de crédito y la lista de patrones del dominio.

## Señales de alarma propias

- AUC mayor a 0.90 en un score de originación. No es imposible, pero hay que demostrar que no hay leakage antes de creerlo.
- Una variable con IV mayor a 0.5.
- Variables con nombres de resultado: `mora`, `atraso`, `castigo`, `estado_final`, `dias_vencido`, `cobranza`, `recupero`, `refinanciado`.

## Fuentes típicas en crédito

| Fuente | Ejemplo | Cómo evitarla |
|---|---|---|
| Desempeño del propio préstamo | Saldo, atraso o pagos del préstamo que se está evaluando | Fecha de corte estricta = fecha de la solicitud |
| Buró "foto actual" | Datos de buró consultados hoy, no a la fecha de la solicitud | Usar la consulta histórica guardada en la evaluación o snapshots del buró a la fecha |
| Variables de proceso | Fecha de desembolso, monto aprobado, oferta final, analista asignado | Excluir: son consecuencia de la decisión |
| Agregados de comportamiento mal cortados | "Atraso máximo en 6 meses" calculado hasta hoy | Calcular hasta la fecha de corte |
| Refinanciaciones posteriores | Marca de refinanciación usada como feature | Es parte del target, no una variable |

## Lista de patrones

`domains/credit-scoring/checks/forbidden_columns.example.txt` tiene los patrones de crédito y cobranzas. Para un proyecto, combinarla con la lista genérica de `ml-foundations/checks/forbidden_columns.example.txt` en un `forbidden_columns.txt` en la raíz del proyecto y ajustarla a los nombres reales de las columnas.
