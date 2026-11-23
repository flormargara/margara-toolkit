# Chequeos

## Propios de cobranzas (`collections/checks/`)

- `check_training_population.py`: desde el inicio de la gestión guiada por el modelo, el universo de entrenamiento y evaluación tiene solo filas de control. Con `--target-kind autocura`, todas las filas tienen que ser de control o sin gestión, de cualquier fecha. Las filas anteriores al modelo se aceptan para pase de tramo y se pide documentar qué gestión recibieron.
- `check_control_group.py`: sobre el registro de asignaciones, verifica que el control sea persistente (ninguna cuenta cambia de grupo), que la proporción por rating sea la esperada (contando cada cuenta una vez) y que el control alcance para reentrenar (`--min-control-rows`, `--min-control-events`).

## De crédito (`credit-scoring/checks/`)

- `check_ratings.py` con `--where grupo=control`: monotonía y calibración de los ratings medidas sobre el control.
- `roll_rate.py` si hay que justificar qué tramo de atraso es el evento.

## Genéricos (`ml-foundations/checks/`)

- `check_universe.py` para el universo por fecha de entrada al tramo.
- `check_dataset.py` antes de modelar.
- `check_leakage.py` con un `forbidden_columns.txt` que combine la lista genérica, la de crédito (`credit-scoring/checks/forbidden_columns.example.txt`, que ya incluye gestiones, contactos y promesas del episodio actual) y los nombres reales del proyecto.
- `psi.py` para estabilidad del score y de las variables.
- `check_concentration.py` sobre las importancias del modelo.
