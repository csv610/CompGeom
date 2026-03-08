# `euler_characteristic.py`

Purpose: CLI for computing the Euler characteristic of a triangle mesh.

Algorithm:
- parses vertices and triangle indices
- counts unique vertices, unique undirected edges, and faces
- computes `chi = V - E + F`

Input:
- point section: `id x y` or implicit ids from `x y`
- line `T`
- triangle section: three point ids per line

Output: counts for vertices, edges, faces, and the Euler characteristic.

Assumptions: triangles reference valid points.
