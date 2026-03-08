# `generate_concave_shapes.py`

Purpose: CLI for generating a simple polygon that may be concave.

Algorithm:
- calls `polygon_utils.generate_simple_polygon`
- samples random points
- sorts them around the centroid by polar angle

Input: script-level parameters or defaults only.

Output: generated polygon vertices.

Assumptions: output is simple in typical cases but not a guaranteed benchmark generator.
