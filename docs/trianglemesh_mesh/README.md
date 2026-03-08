# `trianglemesh/mesh.py`

Purpose: reusable topological mesh helpers.

Algorithms:
- collects unique vertices from triangle lists
- collects unique undirected edges from triangle adjacency implied by faces
- computes Euler characteristic with `V - E + F`

Inputs: list of triangle tuples `(Point, Point, Point)`.

Outputs: counts or sets derived from the mesh topology.
