# Golden rules de collections

Catálogo de reglas de `domains/collections` en el formato de golden rules de ai-mllc. Se compone después de `ml-foundations` y `credit-scoring`: `compose.py ml-foundations credit-scoring collections`. Acá solo va lo propio de cobranzas; de las de crédito, las de originación (por ejemplo `cr-sesgo-de-seleccion` o `cr-punto-de-corte`) se evalúan como `no_aplica` si no corresponden. Cada regla remite al archivo del toolkit que la explica. Los chequeos viven en `~/projects/margara-toolkit/domains/collections/checks/` y `~/projects/margara-toolkit/domains/credit-scoring/checks/`; el código de salida 0 es `cumple`, 1 es `no_cumple`, y si no se pudo correr por falta de insumos es `evidencia_insuficiente`.

## co-problem-framing (v1)

- fuerza: bloqueante
- etapa: intake
- mecanismo: discusion
- estado: active

Acordar con el Data Scientist, y que él lo valide con cobranzas, y registrar en el frame: tramo de entrada al universo, evento y horizonte, productos (y si van en modelos separados), acción por segmento de rating, métrica de éxito de negocio y restricciones operativas (capacidad, horarios, canales, días hábiles). Ver `domains/collections/knowledge/00-flujo.md`, "Problem framing".

## co-vigente-sobre-control (v1)

- fuerza: alerta
- etapa: understand
- mecanismo: atestacion
- estado: active

Presentar el desempeño del modelo o la segmentación vigente medido sobre el grupo de control, y las curvas de pago por segmento (qué proporción se regulariza sola en el día 3, 5, 10). Si no hay control, decirlo: el desempeño medido sobre cuentas gestionadas mezcla riesgo y gestión. Ver `00-flujo.md`, "Etapas", y `01-target-y-features.md`, "Curvas de pago".

## co-universo-por-entrada-al-tramo (v1)

- fuerza: bloqueante
- etapa: observe
- mecanismo: atestacion
- estado: active

El universo tiene una fila por cuenta y fecha de entrada al tramo, que es la `fecha_corte`. Atestar: exclusiones de cuentas con otra obligación más atrasada (si la acción es por cliente), cómo se tratan las entradas repetidas de un cliente (split por cliente o una por cliente con hash determinista) y la identificación de cuentas con débito automático. Ver `01-target-y-features.md`, "Universo".

## co-target-definido (v1)

- fuerza: bloqueante
- etapa: observe
- mecanismo: atestacion
- estado: active

El target queda escrito: pase de tramo (peor tramo alcanzado en el horizonte) o autocura (regularización sin gestión humana antes de cierto día), con qué es "regularizar" (pago mínimo, total del vencido o volver a 0 días). El horizonte está cumplido para todas las filas de entrenamiento: es el `--horizon-days` de `ml-integridad-temporal`. Ver `01-target-y-features.md`, "Target".

## co-entrenar-solo-con-control (v1)

- fuerza: bloqueante
- etapa: observe
- mecanismo: check_determinista
- estado: active

Correr `python3 check_training_population.py <universo.csv> --model-start <AAAA-MM-DD>` (con `--target-kind autocura` si el target es autocura, y `--split-col` si hay filas de scoring). Desde el inicio de la gestión guiada por el modelo, solo entran filas de control; con autocura, solo control o sin gestión, de cualquier fecha. Para el primer modelo, sin control propio, documentar qué gestión recibieron las cuentas de la historia. Ver `00-flujo.md`, "Entrenar solo con el grupo de control".

## co-sin-gestiones-del-episodio (v1)

- fuerza: bloqueante
- etapa: features
- mecanismo: atestacion
- estado: active

Ninguna feature usa gestiones, contactos, promesas, asignación a agencia ni la fecha de primera gestión del episodio de mora actual: ocurren después de la decisión. Las gestiones de episodios previos sí valen. El `forbidden_columns.txt` del proyecto incluye esos nombres. Ver `01-target-y-features.md`, "Features".

## co-baseline-segmentacion-vigente (v1)

- fuerza: bloqueante
- etapa: model
- mecanismo: atestacion
- estado: active

Entre los baselines está la segmentación vigente de cobranzas (por ejemplo, reglas por días de atraso y monto). El modelo la mejora en la métrica que importa a la operación, no solo en AUC; si no la mejora, decirlo. Ver `01-target-y-features.md`, "Baselines".

## co-ratings-sobre-control (v1)

- fuerza: bloqueante
- etapa: model
- mecanismo: check_determinista
- estado: active

Correr `python3 check_ratings.py <evaluacion.csv> --order <1,2,3,...> --expected <...> --where grupo=control`: monotonía, tamaño y calibración de los ratings medidos sobre el control (error de calibración acotado, por ejemplo ±5 puntos). FAIL es `no_cumple`. Ver `00-flujo.md`, "Métricas".

## co-metricas-separadas (v1)

- fuerza: alerta
- etapa: model
- mecanismo: atestacion
- estado: active

Las métricas del modelo (AUC, KS, calibración por rating, sobre el control) se presentan separadas de las de impacto (tratamiento contra control, con intención de tratar: pase de tramo, autocura, recupero, días hasta regularizar) y de las de costo (contactos por cuenta, costo por segmento, gestión humana en riesgo alto). El cociente entre agravamiento del control y del tratado mide el impacto de la gestión, no la discriminación. Ver `00-flujo.md`, "Métricas".

## co-backtest (v1)

- fuerza: alerta
- etapa: deploy
- mecanismo: atestacion
- estado: active

Antes del piloto, correr el modelo sobre el día o el mes anterior con los datos congelados y validar el resultado con cobranzas: volúmenes por rating, cuentas que caen en cada acción, casos que llamen la atención. Ver `00-flujo.md`, "Etapas".

## co-grupo-de-control (v1)

- fuerza: bloqueante
- etapa: deploy
- mecanismo: check_determinista
- estado: active

Correr `python3 check_control_group.py <asignaciones.csv> --expected <rating=proporción,...> --target-col <target> --min-control-events <n>` sobre el registro de asignaciones del piloto. El control es persistente, tiene la proporción esperada por rating y alcanza para medir impacto y para reentrenar. Documentar qué recibe el control como mínimo (por ejemplo, avisos regulatorios). Ver `00-flujo.md`, "Grupo de control".

## co-ventanas-de-espera (v1)

- fuerza: alerta
- etapa: deploy
- mecanismo: discusion
- estado: active

La ventana de espera de cada segmento antes de la gestión humana se acuerda con el Data Scientist y cobranzas a partir de las curvas de pago por rating y de la capacidad operativa, no de una regla fija. Registrar la ventana elegida por segmento. Ver `01-target-y-features.md`, "Curvas de pago".

## co-operacion-con-alertas (v1)

- fuerza: alerta
- etapa: deploy
- mecanismo: discusion
- estado: active

Acordar la operación: inferencia diaria en días hábiles a una hora fija, entrenamiento y monitoreo mensuales con la regla de promoción, y alertas ante dataset vacío, caída de volumen, fallas de lectura, discrepancias en joins o fallas de envío, con un procedimiento de reenvío. Ver `00-flujo.md`, "Operación".
