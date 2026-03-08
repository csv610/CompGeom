# `point_in_polygon.py`

Purpose: CLI for point-in-polygon testing.

Algorithm:
- first checks whether the query point lies exactly on an edge
- otherwise applies ray casting across polygon edges

Input:
- first line: query point `x y`
- remaining lines: polygon vertices `x y`

Output: whether the point is inside or outside the polygon.
