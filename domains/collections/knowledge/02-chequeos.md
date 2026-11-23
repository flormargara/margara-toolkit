# Chequeos

Este dominio usa los chequeos de `domains/credit-scoring/checks/`:

- `check_universe.py` para el universo por fecha de entrada al tramo.
- `check_leakage.py` con un `forbidden_columns.txt` que incluya gestiones, contactos y promesas del episodio actual.
- `psi.py` para estabilidad del score y de las variables.
- `check_concentration.py` sobre las importancias del modelo.
