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

This installs both the `compgeom` Python package and the command-line utility.

---

## Quick Start: Command-Line Interface

The library provides a unified `compgeom` command.

### Polygon Analysis
```bash
# Identify concave parts of a polygon
compgeom identify_concave_parts --poly 0 0 10 0 10 10 5 5 0 10 --output concave.png

# Decompose a polygon into convex pieces
compgeom convex_decomposition --poly 0 0 10 0 10 10 5 5 0 10 --output pieces.png
```

### Mesh Operations
```bash
# Convert a triangle mesh to a quad mesh
compgeom simple_tri2quads --input model_tri.obj --output model_quad.obj

# Refine a mesh uniformly until no triangle > 1% of total area
compgeom mesh_refinement --input model.obj --max_area 0.01 --output refined.obj

# Reorder mesh vertices using RCM to reduce bandwidth
compgeom mesh_reordering --input model.obj --target vertices --output reordered.obj
```

### Geometric Sampling & Voxelization
```bash
# Voxelize an OBJ model with interior filling
compgeom mesh_voxelization --input model.obj --voxel_size 0.05 --fill --method native

# Find the largest empty circle within a convex hull
compgeom largest_empty_circle --points 0 0 10 0 10 10 0 10 5 5 --output lec.png
```

---

## Quick Start: Python API

### Polygon Resampling & Smoothing
```python
from compgeom.polygon import PolygonalMeanCurvatureFlow

# Resample a polygon to 100 uniform segments and smooth it toward a circle
resampled = PolygonalMeanCurvatureFlow.resample_polygon(my_points, n_points=100)
smoothed = PolygonalMeanCurvatureFlow.smooth(resampled, iterations=200)
```

### Advanced Mesh Reordering
```python
from compgeom.mesh import CuthillMcKee

# Apply RCM reordering to elements
new_indices = CuthillMcKee.reorder_elements(my_mesh)
```

### High-Performance Point Cloud Simplification
```python
from compgeom.spatial import PointSimplifier

# Simplify millions of points using Voxel Grid decimation
# Ratio is relative to the bounding box diagonal
simplified_points = PointSimplifier.simplify(large_point_set, ratio=0.001)
```

---

## Development & Testing

Run the full test suite using `pytest`:

```bash
pytest tests
```

The repository uses GitHub Actions for continuous integration, automatically validating all 30+ core geometric tests on every push.
