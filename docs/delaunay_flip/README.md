# `delaunay_flip.py`

Purpose: CLI for improving a triangle mesh with Delaunay edge flips.

Algorithm:
- reads points and triangle indices
- builds triangle adjacency with `triangulation.build_topology`
- repeatedly flips non-Delaunay interior edges with `triangulation.delaunay_flip`

Input:
- point section: `id x y` or implicit ids from `x y`
- line `T`
- triangle section: three point ids per line

Output: updated triangle list after flipping.

Assumptions: input triangles form a valid planar triangulation.
