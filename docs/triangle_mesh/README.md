# `triangle_mesh.py`

Purpose: CLI for generating a triangle mesh from a 2D point set.

Algorithm:
- reads points
- calls `triangulation.triangulate`
- current implementation uses incremental Bowyer-Watson style insertion with a super-triangle

Input: one `x y` point per line.

Output: triangles listed by point ids plus any skipped points.
