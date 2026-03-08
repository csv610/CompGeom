# `line_arrangement.py`

Purpose: computes a planar arrangement induced by line segments.

Algorithm:
- finds pairwise segment intersections
- splits segments at all discovered intersection points
- builds a planar adjacency graph
- traces bounded faces as polygons

Input: one segment per line as `x1 y1 x2 y2`.

Output:
- all intersection points
- all non-intersecting split segments
- bounded polygons formed by the arrangement

Assumptions: intended for ordinary planar segment arrangements, not heavily degenerate overlap cases.
