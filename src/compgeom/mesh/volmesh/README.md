# Volumetric Mesh and Voronoi Diagrams (volmesh)

This package provides data structures and algorithms for 3D volumetric meshes and Voronoi diagrams.

## Features

- **PolyhedralMesh**: A robust data structure for 3D meshes composed of arbitrary polyhedral cells.
- **VoronoiDiagram3D**: Computes the 3D Voronoi diagram for a set of points using the Delaunay Dual property. Supports unbounded diagrams (including super-tetrahedron vertices for infinite cells).
- **BoundedVoronoi3D**: Computes bounded 3D Voronoi diagrams using an optimized iterative plane-clipping algorithm ($O(N)$ with Delaunay neighbors). Supports:
  - **Box Boundaries** (`from_box`)
  - **Sphere Boundaries** (`from_sphere`)
  - **Cylinder Boundaries** (`from_cylinder`)
- **Validation**: Built-in verification for Voronoi mesh properties including planarity, convexity, and the empty-sphere property.

## Usage

### Basic Voronoi Diagram
```python
from compgeom.kernel import Point3D
from compgeom.mesh.volmesh.voronoi_3d import VoronoiDiagram3D

points = [Point3D(0,0,0), Point3D(1,0,0), Point3D(0,1,0), Point3D(0,0,1), Point3D(0.2,0.2,0.2)]
voronoi = VoronoiDiagram3D()
mesh = voronoi.compute(points)

print(f"Vertices: {len(mesh.vertices)}")
print(f"Cells: {len(mesh.cells)}")
```

### Bounded Voronoi (Box)
```python
from compgeom.kernel import Point3D
from compgeom.mesh.volmesh.bounded_voronoi_3d import BoundedVoronoi3D

points = [Point3D(25, 50, 50), Point3D(75, 50, 50)]
# Create a 100x100x100 box boundary
bv = BoundedVoronoi3D.from_box(Point3D(0, 0, 0), Point3D(100, 100, 100))
mesh = bv.compute(points)
```

## Performance

The implementation is optimized for high performance using Delaunay neighbor-only clipping for bounded diagrams.

| Points ($N$) | Unbounded (s) | Bounded Box (s) |
| :--- | :--- | :--- |
| 10 | 0.0003 | 0.0007 |
| 100 | 0.0009 | 0.0011 |
| 1,000 | 0.0052 | 0.0068 |
| 10,000 | 0.0339 | 0.0628 |
| 100,000 | 0.6217 | 1.0265 |

Benchmarks were performed on a standard development machine using `bench_voronoi_3d.py`.

## Validation

Use `validate_voronoi_mesh` to ensure the geometric integrity of the resulting mesh:
```python
from compgeom.mesh.volmesh.volmesh_validation import validate_voronoi_mesh

is_valid, errors = validate_voronoi_mesh(mesh)
if not is_valid:
    print(f"Errors found: {errors}")
```
