# `polygon_boolean_operations.py`

Purpose: boolean operations on simple polygon shapes.

Algorithms:
- splits polygon edges at intersections
- classifies edge fragments or arrangement faces
- reconstructs result polygons for `intersection`, `union`, `difference`, and `xor`

Input:
- first line: operation name
- then two count-prefixed polygons

Output: one or more result polygons, with orientation shown in the printout.

Assumptions:
- simple polygons
- not a fully robust industrial clipping engine for degenerate cases
