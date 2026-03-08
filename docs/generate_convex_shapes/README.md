# `generate_convex_shapes.py`

Purpose: CLI for generating random convex polygons.

Algorithm:
- samples random points
- computes the convex hull with monotone chain

Input: script-level parameters or defaults only.

Output: convex polygon vertices in boundary order.

Assumptions: convex hull size may be smaller than the requested sample count.
