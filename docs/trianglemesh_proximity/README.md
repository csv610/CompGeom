# `trianglemesh/proximity.py`

Purpose: reusable proximity, intersection, and enclosing-shape helpers.

Algorithms:
- GJK-style minimum distance between convex polygons
- divide-and-conquer closest pair
- segment intersection by orientation tests
- rotating calipers farthest pair
- circle construction from 2 or 3 points
- Welzl minimum enclosing circle recursion
- Minkowski sum by angular edge merge

Inputs: `Point` sets or convex polygons depending on the routine.

Outputs: distances, point pairs, circles, or derived polygons.
