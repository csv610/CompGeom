# `closest_pair.py`

Purpose: CLI for the planar closest-pair problem.

Algorithm:
- reads 2D points
- calls `proximity_utils.closest_pair`
- uses divide-and-conquer with an x-sorted split and strip check

Input: one `x y` point per line.

Output: closest point pair and Euclidean distance.

Assumptions: standard 2D point set, no special handling for malformed lines beyond skipping them.
