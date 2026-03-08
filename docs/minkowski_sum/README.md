# `minkowski_sum.py`

Purpose: CLI for Minkowski sum of two polygons.

Algorithm:
- orients both polygons consistently
- rotates each polygon so the lowest vertex comes first
- merges edge directions in angular order

Input: two polygons in the script's existing count-prefixed format.

Output: vertices of the Minkowski sum polygon.

Assumptions: polygons should be convex for the implemented merge logic.
