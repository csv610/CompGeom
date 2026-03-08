# `art_gallery_problem.py`

Purpose: command-line front end for solving the art gallery problem on a simple polygon.

Algorithm:
- reads polygon vertices from standard input
- triangulates the polygon with ear clipping via `polygon_utils.solve_art_gallery`
- 3-colors the triangulation graph
- returns the smallest color class as guard vertices

Input: one `x y` vertex per line in polygon order.

Output: number of guards and the chosen guard vertices.

Assumptions:
- polygon is simple
- vertex order follows the polygon boundary
