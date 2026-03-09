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
    - Point Simplification (Voxel Grid Decimation)
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
# This step is critical for numerical stability in the flow algorithm
resampled = PolygonalMeanCurvatureFlow.resample_polygon(polygon, n_points=100)

# 3. Apply Mean Curvature Flow (MCF)
# iterations: higher values lead closer to a perfect circle
# time_step (dt): controls the 'speed' of evolution
# fix_centroid: ensures the shape doesn't drift during evolution
smoothed = PolygonalMeanCurvatureFlow.smooth(
    resampled, 
    iterations=200, 
    time_step=0.1, 
    fix_centroid=True
)

print(f"Original vertices: {len(polygon)}, Smoothed vertices: {len(smoothed)}")
```

### 2. High-Performance Point Cloud Simplification
**Objective:** Reduce a massive point set (billions of points) to a representative set based on a spatial density threshold. Uses a Voxel Grid algorithm for $O(N)$ performance.

```python
from compgeom.geometry import Point3D
from compgeom.spatial import PointSimplifier

# Assume 'billions_of_points' is a large generator/iterator of Point3D objects
# To save memory, we can stream points directly into the simplifier

# ratio=0.001 means points closer than 0.1% of the bounding box diagonal will be merged
# This algorithm checks all 26 neighboring voxel cells for true Euclidean distance enforcement
simplified = PointSimplifier.simplify(billions_of_points, ratio=0.001)

print(f"Reduced points from billions to {len(simplified)}")
```

### 3. Mesh Reordering for Bandwidth Reduction (RCM)
**Objective:** Reorder vertices or elements of a mesh to minimize the bandwidth of the resulting adjacency matrix. This significantly speeds up sparse linear solvers used in Finite Element Analysis (FEA) or Fluid Dynamics (CFD).

```python
from compgeom.mesh import OBJFileHandler, TriangleMesh, CuthillMcKee

# 1. Load a high-resolution mesh
vertices, faces = OBJFileHandler.read("engine_part.obj")
mesh = TriangleMesh(vertices, faces)

# 2. Compute Reverse Cuthill-McKee (RCM) permutation
# This reorders vertices to keep adjacent indices as close as possible
new_v_indices = CuthillMcKee.reorder_vertices(mesh)

# 3. Create optimized mesh
# (Internal logic updates all face connectivity to match the new numbering)
optimized_vertices = [mesh.vertices[i] for i in new_v_indices]
inv_map = {old: new for new, old in enumerate(new_v_indices)}
optimized_faces = [tuple(inv_map[v] for v in f) for f in mesh.faces]

optimized_mesh = TriangleMesh(optimized_vertices, optimized_faces)
```

### 4. Advanced Circle Packing
**Objective:** Optimally fill an arbitrary polygon boundary with circles of a specific radius. Uses a hexagonal lattice approach for maximum packing density (~90.6%).

```python
from compgeom.polygon import CirclePacker, generate_simple_polygon

# 1. Generate or define a container boundary
container = generate_simple_polygon(n_points=12, x_range=(0, 100), y_range=(0, 100))

# 2. Pack circles of radius 2.5
centers = CirclePacker.pack(container, radius=2.5)

# 3. Calculate metrics
efficiency = CirclePacker.calculate_efficiency(container, centers, radius=2.5)

print(f"Packed {len(centers)} circles with {efficiency:.2f}% coverage.")
```

### 5. Mesh Voxelization (Surface & Volume)
**Objective:** Convert a 3D triangular mesh into a discrete volumetric representation (Voxels). Supports both shell-only and solid-filled modes.

```python
from compgeom.mesh import OBJFileHandler, MeshVoxelizer

# 1. Load mesh
vertices, faces = OBJFileHandler.read("sphere.obj")

# 2. Voxelize with a grid size of 0.01 units
# fill_interior=True will use a scanline algorithm to fill the volume
voxels = MeshVoxelizer.voxelize_native(
    vertices, 
    faces, 
    voxel_size=0.01, 
    fill_interior=True
)

print(f"Total volume represented by {len(voxels)} voxels.")
```

### 6. Davenport-Schinzel Sequences (Lower Envelopes)
**Objective:** Identify the sequence of segments visible from "minus infinity" along the Y-axis. This is a foundational problem in algorithmic motion planning and visibility.

```python
from compgeom.geometry import Point
from compgeom.sequences import DavenportSchinzel

# Define overlapping line segments (x1, y1, x2, y2)
segments = [
    (Point(0, 5), Point(10, 5)),  # Horizontal line at y=5
    (Point(2, 8), Point(8, 2)),   # Diagonal line crossing through
    (Point(4, 2), Point(6, 10))   # Sharp diagonal line
]

# Calculate the combinatorial sequence of IDs appearing on the lower envelope
sequence = DavenportSchinzel.calculate_sequence(segments)

# Result: [0, 2, 0, 1, 0] (Indices of segments as they appear left-to-right)
print("Lower envelope sequence:", " -> ".join(map(str, sequence)))
```

---

## Command-Line Interface (CLI) Quick-Start

The library provides a single entry point `compgeom` for easy access to all algorithms.

| Command | Description | Example |
| :--- | :--- | :--- |
| `visualize_curve` | Generate space-filling curve paths | `compgeom visualize_curve hilbert --level 3 --output path.png` |
| `mesh_refinement` | Increase mesh resolution | `compgeom mesh_refinement --input in.obj --max_area 0.01 --output out.obj` |
| `rectangle_packer` | Pack rectangles into containers | `compgeom rectangle_packer --dims 10 20 5 5 15 10 --shape square` |
| `mesh_voxelization` | Convert 3D mesh to voxels | `compgeom mesh_voxelization --input model.obj --voxel_size 0.05 --fill` |
| `mesh_reordering` | Apply RCM renumbering | `compgeom mesh_reordering --input in.obj --target vertices --output out.obj` |
| `circle_packing` | Pack circles into polygons | `compgeom circle_packing --poly 0 0 10 0 10 10 0 10 --radius 1.0` |

---

## Development & Testing

The library is strictly validated with a comprehensive test suite.

```bash
# Run all tests
pytest tests

# Run with coverage report
pytest --cov=compgeom tests
```

The repository uses GitHub Actions for CI, ensuring every push is verified against 30+ core geometric benchmarks.
