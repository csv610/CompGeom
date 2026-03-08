# `convex_partition.py`

Purpose: CLI for partitioning a simple polygon into convex parts.

Algorithm:
- uses `polygon_utils.hertel_mehlhorn`
- first ear-clips the polygon into triangles
- then merges compatible adjacent triangles using a Hertel-Mehlhorn style heuristic

Input: one `x y` polygon vertex per line.

Output: convex partitions reported as vertex-index sets.

Assumptions:
- polygon is simple
- output is heuristic convex partitioning, not necessarily minimum-cardinality
