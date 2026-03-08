# `trianglemesh/triangulation.py`

Purpose: triangulation, Delaunay, and Voronoi algorithms.

Algorithms:
- incremental point-set triangulation using a super-triangle and Bowyer-Watson style cavity replacement
- constrained Delaunay triangulation for polygonal domains with optional holes
- triangle adjacency construction from shared edges
- iterative Delaunay edge flipping with an in-circle test
- dynamic Delaunay insertion with local edge legalization
- Voronoi cell construction by clipping against perpendicular-bisector half-planes

Inputs: point sets, triangle lists, or boundary polygons depending on the routine.

Outputs: triangle meshes, adjacency-aware mesh objects, or clipped Voronoi cells.

Assumptions: 2D floating-point geometry, mostly educational rather than fully robust computational-geometry kernels.

Notes:
- `constrained_delaunay_triangulation` preserves polygon-domain boundary constraints and legalizes only unconstrained interior edges
- the constrained implementation is intended for simple polygonal domains rather than arbitrary PSLGs
