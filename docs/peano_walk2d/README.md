# `peano_walk2d.py`

Purpose: CLI for mapping Peano curve indices to 2D coordinates.

Algorithm:
- decodes the base-9 digit sequence level by level
- applies row/column flips induced by previous turns

Input: Peano index and level via command-line arguments.

Output: `(x, y)` coordinate.
