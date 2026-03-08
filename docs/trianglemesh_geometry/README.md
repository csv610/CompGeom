# `trianglemesh/geometry.py`

Purpose: low-level 2D geometry primitives and predicates shared across the project.

Algorithms and utilities:
- tolerant `Point` equality and hashing
- cross and dot products
- vector subtraction and norms
- line-line intersection
- polygon half-plane clipping
- point-on-segment and point-in-triangle predicates
- in-circle predicate for Delaunay methods

Inputs/Outputs: mostly `Point` objects and scalar geometric values.

Assumptions: floating-point geometry with epsilon-based comparisons.
