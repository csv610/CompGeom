# Angle-Bounded Remeshing

Angle-bounded remeshing is a surface mesh refinement process that improves the quality of a triangular mesh by enforcing specific bounds on the internal angles of all triangles.

## Overview

High-quality triangular meshes are essential for accurate physical simulations. Small or large angles can lead to numerical instability. This remeshing technique (inspired by TriWild) iteratively modifies the mesh topology and geometry to improve the overall quality, targeting a minimum angle of $30^\circ$ and a maximum angle of $120^\circ$.

## Implementation Details

The `AngleBoundedRemesher` in `CompGeom` uses a sequence of local mesh operations:
1.  **Edge Splits**: Long edges are split to reduce triangle size.
2.  **Edge Collapses**: Short edges are collapsed to remove small or sliver triangles.
3.  **Edge Flips**: Edges are flipped to maximize the minimum angle in the local quadrilateral.
4.  **Vertex Smoothing**: Vertices are moved to their local centroids (Laplacian smoothing) to create more uniform distributions.

## Usage

```python
from compgeom.mesh.surface.angle_bounded_remesher import AngleBoundedRemesher
from compgeom.mesh import TriMesh

mesh = TriMesh.from_file("input.obj")
remesher = AngleBoundedRemesher(mesh, min_angle=30.0, max_angle=120.0)
refined_mesh = remesher.remesh(iterations=5)
```

## References
- Hu, Y., et al. "TriWild: Robust Remeshing with Angle Bounds." ACM Transactions on Graphics (SIGGRAPH), 2021.
- Botsch, M., et al. "Polygon Mesh Processing." CRC Press, 2010.
