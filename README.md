# CompGeom: Computational Geometry Library

A Python library and command-line suite for geometric modeling, mesh processing, and spatial analysis.

## Table of Contents

### Part I: Foundations & Core Geometry
1. **Introduction**
   - Overview
   - Installation
2. **Geometric Primitives**
   - Point and Point3D
   - Geometric Predicates (Orientation, Incircle)
   - Fundamental Calculations (Cross Product, Dot Product, Distances)
3. **High-Level Shape Objects**
   - 2D Shapes (Triangle, Square, Rectangle, Circle)
   - 3D Shapes (Sphere, Cube, Cuboid, Tetrahedron, Hexahedron)
   - Linear Objects (LineSegment, Ray, Plane)

### Part II: Polygon Processing
4. **Basic Polygon Algorithms**
   - Orientation & Properties (Area, Centroid, Diameter)
   - Containment, Visibility & Kernel
   - Convex Hull (Graham Scan, Monotone Chain)
5. **Advanced Polygon Transformations**
   - Polygon Smoothing (Mean Curvature Flow)
   - Polygon Decomposition (Triangulation, Convex, Monotone, Trapezoidal, Visibility)
   - Concave Part Identification (Reflex Vertices)
   - Random Polygon Generation (PolygonGenerator)
6. **Spatial Polygon Operations**
   - Circle Packing (Hexagonal Grid)
   - Distance Maps (Eikonal Equation / Fast Sweeping Method)
   - Medial Axis & Skeletal Structures
   - Planar Subdivisions (DCEL)

### Part III: Mesh Processing & Modeling
7. **Mesh Architecture**
   - Mesh Types (Triangle, Quad, Tet, Hex)
   - Mesh Topology & Adjacency Queries
   - Mesh Loading (STL, OFF, OBJ Support via `MeshImporter`)
8. **Mesh Refinement & Reordering**
   - Triangle Mesh Refinement (Linear & Uniform)
   - Bandwidth Reduction (Reverse Cuthill-McKee)
   - Nodal Renumbering (`reorder_nodes`)
9. **Mesh Optimization**
   - Mesh Coloring (Vertex & Element)
   - Triangle-to-Quad Conversion
   - **Mesh Topology Transfer (Harmonic Mapping)**
10. **Volumetric Modeling**
    - Mesh Voxelization (Native & OpenVDB)
    - Mesh I/O (STL, OFF, OBJ Support)

### Part IV: Spatial Algorithms & Visualization
11. **Combinatorial Sequences**
    - Davenport-Schinzel Sequences (Lower Envelopes)
12. **Point Cloud Operations**
    - Point Sampling (Circle, Rectangle, Triangle, Cube, Sphere)
    - Protected Point Simplification (Voxel Grid Decimation)
    - Closest/Farthest Pair Analysis
13. **Grid & Path Generation**
    - Space-Filling Curves (Hilbert, Peano, Morton, ZigZag, Sweep)
    - Random Walks (2D, 3D, Self-Avoiding)
14. **Visualization & Export**
    - SVG Generation
    - PNG Export (System Utility Support)

---

## Installation

Install the library in editable mode for development:

```bash
pip install -e .
```

---

## Detailed Examples & Explanations

Complete Python examples for the algorithms listed in this README are collected in [docs/algorithm_examples.md](docs/algorithm_examples.md).

### 1. Polygon Generation & Smoothing
**Objective:** Generate a random irregular polygon and transform it into a circle while preserving its perimeter.

```python
from compgeom.polygon import PolygonGenerator, PolygonalMeanCurvatureFlow

# 1. Generate a random concave polygon
polygon = PolygonGenerator.concave(n_points=20)

# 2. Resample to 100 uniform points
resampled = PolygonalMeanCurvatureFlow.resample_polygon(polygon, n_points=100)

# 3. Apply Mean Curvature Flow (MCF)
smoothed = PolygonalMeanCurvatureFlow.smooth(resampled, iterations=200)
```

### 2. Polygon Decomposition & Kernel
**Objective:** Decompose a polygon into useful substructures and compute its visibility kernel.

```python
from compgeom import Point, Polygon, PolygonDecomposer, polygon_kernel

polygon = [Point(0, 0), Point(4, 0), Point(4, 4), Point(2, 2), Point(0, 4)]

tri_mesh = PolygonDecomposer.triangulate(polygon)
convex_mesh = PolygonDecomposer.convex_decomposition(polygon)
monotone_mesh = PolygonDecomposer.monotone_decomposition(polygon)
trapezoid_mesh = PolygonDecomposer.trapezoidal_decomposition(polygon)
visibility_mesh = PolygonDecomposer.visibility_decomposition(polygon)

kernel = Polygon(polygon).kernel()
kernel2 = polygon_kernel(polygon)
```

### 3. High-Performance Point Cloud Simplification
**Objective:** Reduce a massive point set while protecting specific points from removal.

```python
from compgeom import PointSimplifier

# Protect critical boundary or landmark points
protected = {0, 10, 50}

# ratio=0.001 means grid size is 0.1% of bounding box diagonal
simplified = PointSimplifier.simplify(points, ratio=0.001, protected_ids=protected)
```

### 4. Mesh Topology Transfer
**Objective:** Map the triangulation from one polygonal boundary to a completely different boundary shape while minimizing geometric distortion using **Harmonic Mapping**.

```python
from compgeom.mesh import TriangleMesh, MeshTransfer

# 1. Load a source mesh (e.g., a high-quality grid in a square)
source = TriangleMesh.from_file("square_grid.obj")

# 2. Define a new target boundary (e.g., an L-shape)
target_poly = [Point(0,0), Point(2,0), Point(2,1), Point(1,1), Point(1,2), Point(0,2)]

# 3. Transfer the topology
# This solves the discrete Laplace equation for internal vertex positions
new_mesh = MeshTransfer.transfer(source, target_poly)
```

### 5. Mesh Renumbering & Bandwidth Reduction
**Objective:** Load a mesh and reorder its vertices to optimize matrix bandwidth.

```python
from compgeom.mesh import TriangleMesh, CuthillMcKee

# 1. Load directly from OBJ file
mesh = TriangleMesh.from_file("model.obj")

# 2. Compute Reverse Cuthill-McKee (RCM) permutation
new_indices = CuthillMcKee.reorder_vertices(mesh)

# 3. Apply renumbering (automatically updates all face connectivity)
mesh.reorder_nodes(new_indices)
```

### 6. Mesh Voxelization (Surface & Volume)
**Objective:** Convert a 3D triangular mesh into a solid voxel grid.

```python
from compgeom.mesh import TriangleMesh, MeshVoxelizer

mesh = TriangleMesh.from_file("model.obj")

# fill_interior=True uses a scanline algorithm to fill the volume
voxels = MeshVoxelizer.voxelize(mesh, voxel_size=0.01, fill_interior=True)
```


### 7. Delaunay Triangulation & Mesh Merging
**Objective:** Triangulate a point set using the optimized Edge Flip algorithm and merge it with another mesh.

```python
from compgeom.mesh.trimesh import DelaunayMesher, PlatonicSolid

# 1. Generate points and triangulate using Edge Flip
points = [Point(0,0), Point(1,0), Point(0,1), Point(1,1), Point(0.5, 0.5)]
mesh1 = DelaunayMesher.triangulate(points, algorithm="edge_flip")

# 2. Generate a Platonic Solid (e.g., Tetrahedron)
tetra = PlatonicSolid.tetrahedron(size=2.0)

# 3. Merge meshes (Optimized via Incremental Seeding)
# Note: Merge works best for TriangleMesh objects
merged = DelaunayMesher.merge(mesh1, tetra)
```

### 8. Multi-Format Mesh I/O
**Objective:** Import a mesh from OFF format and export it to STL.

```python
from compgeom.mesh.trimesh import MeshImporter, MeshExporter

# 1. Import
mesh = MeshImporter.import_mesh("model.off")

# 2. Export to various formats
MeshExporter.export_mesh(mesh, "model.obj")
MeshExporter.export_mesh(mesh, "model.stl")
```
---

## Command-Line Interface (CLI) Quick-Start

| Command | Description | Example |
| :--- | :--- | :--- |
| `mesh_transfer` | Map mesh to new boundary | `compgeom mesh_transfer --input sq.obj --output circle.obj` |
| `identify_concave_parts`| Find reflex vertices | `compgeom identify_concave_parts --poly 0 0 10 0 10 10 5 5 0 10` |
| `convex_decomposition` | Decompose a polygon and visualize the convex pieces | `compgeom convex_decomposition --poly ... --output pieces.png` |
| `simple_tri2quads` | Convert triangles to quads | `compgeom simple_tri2quads in.obj out.obj` |
| `point_simplification` | $O(N)$ point cloud decimation | `compgeom point_simplification --n 1000000 --ratio 0.005` |
| `mesh_refinement` | Increase mesh resolution | `compgeom mesh_refinement --input in.obj --max_area 0.01` |
| `mesh_voxelization` | Convert 3D mesh to voxels | `compgeom mesh_voxelization --input model.obj --fill` |

---

## Project Structure

- `src/compgeom/` - Core package:
    - `geo_math/`: geometric primitives and numeric helpers.
    - `polygon/`: polygon algorithms, kernel and visibility queries, decomposition helpers, smoothing, medial axis, and DCEL helpers.
    - `mesh/`: mesh data structures, topology, I/O, refinement, transfer, voxelization, and triangulation helpers.
    - `algo/`: higher-level algorithms such as `PointSimplifier`, `PointSampler`, `DavenportSchinzel`, `RectanglePacker`, and `SpaceFillingCurves`.
    - `graphics/`: SVG/PNG export utilities.
- `src/compgeom/cli/` - CLI script implementations.
- `tests/` - Unit and CLI regression tests for a subset of the library surface.

## Development & Testing

```bash
pytest tests
```
