# `convex_polygon_distance.py`

Purpose: CLI for computing minimum distance between two convex polygons.

Algorithm:
- delegates to `proximity_utils.min_dist_convex_polygons`
- uses a GJK-style search in the Minkowski difference

Input:
- polygon 1
- polygon 2
- exact format follows the script's existing parser expectations

Output: minimum distance between the polygons.

Assumptions: polygons should be convex.
