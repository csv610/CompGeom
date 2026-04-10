# Non-Obtuse Triangulation

Non-Obtuse Triangulation is the process of subdividing a 2D domain into triangles such that no internal angle exceeds $90^\circ$.

## Overview

Most standard triangulation algorithms (including Delaunay) may produce obtuse triangles. For certain numerical simulations (like finite element analysis or fluid dynamics), obtuse triangles can introduce errors or numerical instability. A non-obtuse triangulation ensures that all angles are acute or right angles.

## Implementation Details

In `CompGeom`, the `NonObtuseTriangulator` uses an iterative Steiner point insertion strategy:
1.  **Initial Mesh**: Start with a Delaunay triangulation of the input point set.
2.  **Detection**: Identify triangles with an angle $> 90^\circ$.
3.  **Refinement**: For each obtuse triangle, insert a new vertex (Steiner point) at the midpoint of its longest edge.
4.  **Re-triangulation**: Update the Delaunay triangulation with the new point.
5.  **Iteration**: Repeat until no obtuse triangles remain or a maximum number of Steiner points is reached.

## Usage

```python
from compgeom.mesh.surface.trimesh.non_obtuse_triangulation import NonObtuseTriangulator
from compgeom import Point2D

pts = [Point2D(0, 0), Point2D(10, 0), Point2D(5, 0.1)] # Very obtuse triangle
triangulator = NonObtuseTriangulator(pts)
mesh = triangulator.triangulate(max_steiner=100)
```

## References
- Bern, M., et al. "Provably Good Mesh Generation." Journal of Computer and System Sciences, 1994.
- CG:SHOP 2025 Challenge: "Minimum Non-Obtuse Triangulation."
