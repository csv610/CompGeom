# `graham_scan.py`

Purpose: CLI for convex hull construction.

Algorithm:
- reads points
- calls `polygon_utils.graham_scan`
- sorts points by angle around the anchor point
- pops right turns from the hull stack

Input: one `x y` point per line.

Output: convex hull vertices in order.
