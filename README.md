# CompGeom: Computational Geometry Library

A comprehensive Python library and command-line suite for geometric modeling, mesh processing, and spatial analysis.

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
   - Containment & Visibility
   - Convex Hull (Graham Scan, Monotone Chain)
5. **Advanced Polygon Transformations**
   - Polygon Smoothing (Mean Curvature Flow)
   - Convex Decomposition (Hertel-Mehlhorn)
   - Concave Part Identification (Reflex Vertices)
   - **Random Polygon Generation (PolygonGenerator)**
6. **Spatial Polygon Operations**
   - Circle Packing (Hexagonal Grid)
   - Distance Maps (Eikonal Equation / Fast Sweeping Method)
   - Medial Axis & Skeletal Structures
   - Planar Subdivisions (DCEL)

### Part III: Mesh Processing & Modeling
7. **Mesh Architecture**
   - Mesh Types (Triangle, Quad, Tet, Hex)
   - Mesh Topology & Adjacency Queries
   - **Mesh Loading (OBJ Support via `from_file`)**
8. **Mesh Refinement & Reordering**
   - Triangle Mesh Refinement (Linear & Uniform)
   - Bandwidth Reduction (Reverse Cuthill-McKee)
   - **Nodal Renumbering (`reorder_nodes`)**
9. **Mesh Optimization**
   - Mesh Coloring (Vertex & Element)
   - **Triangle-to-Quad Conversion**
10. **Volumetric Modeling**
    - Mesh Voxelization (Native & OpenVDB)
    - Mesh I/O (OBJ Support)

### Part IV: Spatial Algorithms & Visualization
11. **Combinatorial Sequences**
    - Davenport-Schinzel Sequences (Lower Envelopes)
12. **Point Cloud Operations**
    - Point Sampling (Circle, Rectangle, Triangle, Cube, Sphere)
    - **Protected Point Simplification (Voxel Grid Decimation)**
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

### 2. High-Performance Point Cloud Simplification
**Objective:** Reduce a massive point set while **protecting specific points from removal**.

```python
from compgeom.spatial import PointSimplifier

# Protect critical boundary or landmark points
protected = {0, 10, 50}

# ratio=0.001 means grid size is 0.1% of bounding box diagonal
simplified = PointSimplifier.simplify(points, ratio=0.001, protected_ids=protected)
```

### 3. Mesh Renumbering & Bandwidth Reduction
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

### 4. Triangle-to-Quad Conversion
**Objective:** Transform a triangular mesh into a quadrilateral mesh.

```python
from compgeom.mesh import TriangleMesh, TriangleToQuadConverter

# 1. Load triangle mesh
tri_mesh = TriangleMesh.from_file("input.obj")

# 2. Convert (1-to-3 split algorithm)
quad_mesh = TriangleToQuadConverter.convert(tri_mesh)
```

### 5. Mesh Voxelization (Surface & Volume)
**Objective:** Convert a 3D triangular mesh into a solid voxel grid.

```python
from compgeom.mesh import TriangleMesh, MeshVoxelizer

mesh = TriangleMesh.from_file("model.obj")

# fill_interior=True uses a scanline algorithm to fill the volume
voxels = MeshVoxelizer.voxelize(mesh, voxel_size=0.01, fill_interior=True)
```

---

## Command-Line Interface (CLI) Quick-Start

| Command | Description | Example |
| :--- | :--- | :--- |
| `identify_concave_parts`| Find reflex vertices | `compgeom identify_concave_parts --poly 0 0 10 0 10 10 5 5 0 10` |
| `convex_decomposition` | Split polygon into convex pieces | `compgeom convex_decomposition --poly ... --output pieces.png` |
| `simple_tri2quads` | Convert triangles to quads | `compgeom simple_tri2quads in.obj out.obj` |
| `point_simplification` | $O(N)$ point cloud decimation | `compgeom point_simplification --n 1000000 --ratio 0.005` |
| `mesh_refinement` | Increase mesh resolution | `compgeom mesh_refinement --input in.obj --max_area 0.01` |
| `mesh_voxelization` | Convert 3D mesh to voxels | `compgeom mesh_voxelization --input model.obj --fill` |
| `circle_packing` | Pack circles into polygons | `compgeom circle_packing --poly ... --radius 1.0` |

---

## Development & Testing

```bash
pytest tests
```
