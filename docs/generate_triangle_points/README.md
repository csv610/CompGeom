# `generate_triangle_points.py`

Purpose: CLI for generating points uniformly inside a triangle.

Algorithm:
- uses `polygon_utils.generate_points_in_triangle`
- samples barycentric coordinates with reflection across the unit simplex diagonal

Input: triangle vertices and desired sample count as defined by the script.

Output: sampled interior points.

Assumptions: triangle must be non-degenerate for meaningful output.
