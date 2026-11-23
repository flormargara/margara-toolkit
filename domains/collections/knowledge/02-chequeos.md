# Chequeos

Este dominio usa los chequeos genéricos de `ml-foundations/checks/`:

- `check_universe.py` para el universo por fecha de entrada al tramo.
- `check_leakage.py` con un `forbidden_columns.txt` que combine la lista genérica, la de crédito (`credit-scoring/checks/forbidden_columns.example.txt`, que ya incluye gestiones, contactos y promesas del episodio actual) y los nombres reales del proyecto.
- `psi.py` para estabilidad del score y de las variables.
- `check_concentration.py` sobre las importancias del modelo.
