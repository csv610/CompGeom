# `minimum_bounding_shapes.py`

Purpose: CLI for minimum enclosing shapes of a 2D point set.

Algorithms:
- minimum enclosing circle via randomized Welzl recursion
- minimum bounding box via convex hull plus edge-aligned rotating-calipers search

Input: one `x y` point per line.

Output:
- circle center and radius
- bounding-box center, width, height, area, angle, and corners
