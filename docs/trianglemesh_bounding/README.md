# `trianglemesh/bounding.py`

Purpose: reusable minimum enclosing-shape algorithms for 2D point sets.

Algorithms:
- `minimum_enclosing_circle`: randomized Welzl recursion
- `minimum_bounding_box`: convex hull followed by testing hull-edge-aligned rectangles

Inputs: list of `Point` objects.

Outputs:
- circle as `(center, radius)`
- bounding box as a dictionary with center, width, height, area, angle, and corners

Assumptions: Euclidean 2D point sets.
