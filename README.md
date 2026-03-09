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
6. **Spatial Polygon Operations**
   - Circle Packing (Hexagonal Grid)
   - Distance Maps (Eikonal Equation / Fast Sweeping Method)
   - Medial Axis & Skeletal Structures
   - Planar Subdivisions (DCEL)

### Part III: Mesh Processing & Modeling
7. **Mesh Architecture**
   - Mesh Types (Triangle, Quad, Tet, Hex)
   - Mesh Topology & Adjacency Queries
   - **Mesh Loading (OBJ Support)**
8. **Mesh Refinement & Reordering**
   - Triangle Mesh Refinement (Linear & Uniform)
   - Bandwidth Reduction (Reverse Cuthill-McKee)
9. **Mesh Optimization**
   - Mesh Coloring (Vertex & Element)
   - Triangle-to-Quad Conversion
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

### 1. Polygon Resampling & Smoothing (MCF)
**Objective:** Transform an irregular polygon into a circle while preserving its perimeter. This is useful for shape normalization and organic modeling.

```python
import math
from compgeom.geometry import Point
from compgeom.polygon import PolygonalMeanCurvatureFlow

# 1. Define an irregular star-like polygon
polygon = [
    Point(0, 5), Point(1, 1), Point(5, 0), Point(1, -1),
    Point(0, -5), Point(-1, -1), Point(-5, 0), Point(-1, 1)
]

# 2. Resample to 100 uniform points
resampled = PolygonalMeanCurvatureFlow.resample_polygon(polygon, n_points=100)

# 3. Apply Mean Curvature Flow (MCF)
smoothed = PolygonalMeanCurvatureFlow.smooth(
    resampled, 
    iterations=200, 
    time_step=0.1, 
    fix_centroid=True
)
```

### 2. High-Performance Point Cloud Simplification
**Objective:** Reduce a massive point set to a representative set based on a spatial density threshold, while **protecting specific points from removal**.

```python
from compgeom.geometry import Point3D
from compgeom.spatial import PointSimplifier

# Assume 'points' is a list of Point3D objects
# Protect points with IDs 0, 10, and 50 (e.g., critical boundary or landmark points)
protected = {0, 10, 50}

# ratio=0.001 means grid size is 0.1% of bounding box diagonal
simplified = PointSimplifier.simplify(points, ratio=0.001, protected_ids=protected)

print(f"Original: {len(points)}, Simplified: {len(simplified)}")
```

### 3. Mesh Reordering & Loading
**Objective:** Load a mesh directly from a file and optimize its numbering using Reverse Cuthill-McKee (RCM).

```python
from compgeom.mesh import TriangleMesh, CuthillMcKee

# 1. Load directly from OBJ file
mesh = TriangleMesh.from_file("high_res_model.obj")

# 2. Compute RCM reordering for elements
new_order = CuthillMcKee.reorder_elements(mesh)

# 3. Apply reordering
reordered_faces = [mesh.faces[i] for i in new_order]
optimized_mesh = TriangleMesh(mesh.vertices, reordered_faces)
```

### 4. Advanced Circle Packing
**Objective:** Optimally fill an arbitrary polygon boundary with circles using a hexagonal lattice approach (~90.6% density).

```python
from compgeom.polygon import CirclePacker, generate_simple_polygon

# 1. Generate or define a container boundary
container = generate_simple_polygon(n_points=12, x_range=(0, 100), y_range=(0, 100))

# 2. Pack circles of radius 2.5
centers = CirclePacker.pack(container, radius=2.5)

# 3. Calculate metrics
efficiency = CirclePacker.calculate_efficiency(container, centers, radius=2.5)
```

### 5. Mesh Voxelization (Surface & Volume)
**Objective:** Convert a 3D triangular mesh into a discrete volumetric representation (Voxels).

```python
from compgeom.mesh import OBJFileHandler, MeshVoxelizer

# 1. Load mesh
vertices, faces = OBJFileHandler.read("sphere.obj")

# 2. Voxelize with a grid size of 0.01 units
voxels = MeshVoxelizer.voxelize_native(
    vertices, 
    faces, 
    voxel_size=0.01, 
    fill_interior=True
)
```

### 6. Davenport-Schinzel Sequences (Lower Envelopes)
**Objective:** Identify the sequence of segments visible from "minus infinity" along the Y-axis.

```python
from compgeom.geometry import Point
from compgeom.sequences import DavenportSchinzel

# Define overlapping line segments
segments = [
    (Point(0, 5), Point(10, 5)),
    (Point(2, 8), Point(8, 2)),
    (Point(4, 2), Point(6, 10))
]

# Calculate combinatorial sequence of IDs appearing on the lower envelope
sequence = DavenportSchinzel.calculate_sequence(segments)
```

---

## Command-Line Interface (CLI) Quick-Start

| Command | Description | Example |
| :--- | :--- | :--- |
| `point_simplification` | $O(N)$ point cloud decimation | `compgeom point_simplification --n 1000000 --ratio 0.005 --protected 0 1` |
| `simple_tri2quads` | Convert triangles to quads | `compgeom simple_tri2quads in.obj out.obj` |
| `visualize_curve` | Generate space-filling curves | `compgeom visualize_curve hilbert --level 3 --output path.png` |
| `mesh_refinement` | Increase mesh resolution | `compgeom mesh_refinement --input in.obj --max_area 0.01 --output out.obj` |
| `mesh_voxelization` | Convert 3D mesh to voxels | `compgeom mesh_voxelization --input model.obj --voxel_size 0.05 --fill` |
| `mesh_reordering` | Apply RCM renumbering | `compgeom mesh_reordering --input in.obj --target vertices --output out.obj` |
| `circle_packing` | Pack circles into polygons | `compgeom circle_packing --poly 0 0 10 0 10 10 0 10 --radius 1.0` |

---

## Development & Testing

```bash
# Run all tests
pytest tests
```
