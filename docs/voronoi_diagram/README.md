# `voronoi_diagram.py`

Purpose: CLI for computing clipped Voronoi cells for a set of points.

Algorithm:
- starts with a boundary polygon
- intersects that boundary with half-planes from pairwise perpendicular bisectors

Input: one `x y` point per line, plus optional boundary type argument (`square` or `circle`).

Output: one clipped Voronoi cell per input point.
