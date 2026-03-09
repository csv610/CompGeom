# CompGeom (Computational Geometry)

A comprehensive Python library and command-line tool for computational geometry, mesh operations, spatial algorithms, and visualizations.

## Features

- **Mesh Reordering:** Optimize element and vertex numbering using the Reverse Cuthill-McKee (RCM) algorithm to reduce matrix bandwidth.
- **Mesh Structures:** Support for TriangleMesh, QuadMesh, TetMesh, and HexMesh with topological query support (vertex/element adjacency) via `MeshTopology`.
- **Mesh Refinement:** Subdivide triangular meshes using linear subdivision (midpoint splitting) or uniform refinement (area-ratio based) to increase resolution.
- **Mesh Coloring:** Assign colors to mesh elements (faces/cells) or vertices using a greedy graph coloring algorithm (minimum colors for adjacent components).
- **Geometric Shapes:** Object-oriented representations of Triangle, Square, Rectangle, Circle, Sphere, Cube, Cuboid, Plane, LineSegment, Ray, Tetrahedron, and Hexahedron with properties like area, volume, and centroid.
- **Core Geometry:** Points (2D and 3D), vectors, primitive intersections, geometric predicates (orientation, incircle).
- **Mathematical Utilities:** High-precision orientation and incircle tests, coordinate conversions for space-filling curves, 2D/3D distances, and 2D rotations.
- **Polygon Smoothing:** Transform arbitrary polygons towards a circular shape using discrete Mean Curvature Flow with perimeter preservation.
- **Distance Maps:** Solve the Eikonal equation (|grad u| = 1) using the Fast Sweeping Method to generate distance fields from boundaries.
- **Polygons:** Boolean operations, properties (area, centroid, orientation), visibility, triangulation (ear-clipping, CDT), and shortest paths.
- **Proximity & Bounding:** Closest/farthest pair, Graham scan, monotone chain, minimum bounding box, minimum enclosing circle (Welzl's algorithm), and **Largest Empty Circle**.
- **Davenport-Schinzel Sequences:** Compute the lower envelope of line segments and extract the combinatorial sequence.
- **Space-Filling Curves:** Hilbert, Peano, Morton (Z-order), ZigZag, and Sweep curves with grid cell index output.
- **Point Sampling:** Uniform sampling from circles, rectangles, triangles, line segments, cubes, and spheres.
- **Point Cloud Simplification:** $O(N)$ high-performance grid decimation (Voxel Grid) for simplifying massive datasets (millions/billions of points) based on spatial density.
- **Rectangle Packing:** Area-minimized packing into rectangular or square containers.
- **Circle Packing:** Optimally fit circles of a given radius into an arbitrary closed polygon using hexagonal grid packing with efficiency reporting.
- **Mesh I/O:** Read and write 3D meshes in Wavefront OBJ format, with automatic fan triangulation support.
- **Voxelization:** 3D triangular mesh voxelization using either high-performance OpenVDB (requires `pyopenvdb`) or a robust native surface sampling algorithm.
- **Visualization:** Export paths and shapes to SVG and high-quality PNG (via system tools like `rsvg-convert` or `convert`).
- **Spatial Structures:** KD-Trees, Quadtrees, and Doubly Connected Edge Lists (DCEL).

## Installation

You can install the package directly via pip. It is recommended to use a virtual environment.

```bash
pip install -e .
```

This will also install the `compgeom` command-line utility.

## Usage

### Command-Line Interface

The package exposes a unified command-line tool. You can invoke it using the `compgeom` command.

**Smooth a Polygon (MCF):**
```bash
# Apply 200 iterations of Mean Curvature Flow
compgeom polygonal_mean_curvature_flow --n_points 100 --iterations 200 --output smooth.png
```

**Reorder Mesh Vertices (RCM):**
```bash
compgeom mesh_reordering --input model.obj --target vertices --output reordered.obj
```

**Refine a Mesh (Uniformly):**
```bash
# Refine until no triangle is larger than 1% of total area
compgeom mesh_refinement --input model.obj --max_area 0.01 --output refined.obj
```

**Color Mesh Elements:**
```bash
compgeom mesh_coloring --input model.obj --target elements
```

**Find the Largest Empty Circle:**
```bash
# Find the LEC for a set of points and save visualization
compgeom largest_empty_circle --points 0 0 10 0 10 10 0 10 5 5 --output lec.png
```

**Pack Circles into a Polygon:**
```bash
# Pack circles of radius 1.0 into a 10x10 square
compgeom circle_packing --poly 0 0 10 0 10 10 0 10 --radius 1.0 --output packed.png
```

**Voxelize a 3D Mesh:**
```bash
# Voxelize a cube using native method
compgeom mesh_voxelization --voxel_size 0.1 --method native
```

### Python API

You can use the high-level classes directly in your Python code:

**Polygon Smoothing:**
```python
from compgeom.polygon_smoothing import PolygonalMeanCurvatureFlow

# Resample and smooth a polygon
resampled = PolygonalMeanCurvatureFlow.resample_polygon(my_points, n_points=100)
smoothed = PolygonalMeanCurvatureFlow.smooth(resampled, iterations=100)
```

**Mesh Reordering:**
```python
from compgeom.mesh import CuthillMcKee

# Get new element ordering using RCM
new_indices = CuthillMcKee.reorder_elements(my_mesh)
```

**Mesh Refinement:**
```python
from compgeom.mesh import TriMeshRefiner

# Uniform refinement (ratio-based)
refined_mesh = TriMeshRefiner.refine_uniform(my_mesh, max_area_ratio=0.01)
```

**Largest Empty Circle:**
```python
from compgeom.proximity import LargestEmptyCircle
from compgeom.geometry import Point

points = [Point(0,0), Point(10,0), Point(10,10), Point(0,10), Point(5,5)]
center, radius = LargestEmptyCircle.find(points)
```

**Circle Packing:**
```python
from compgeom.circle_packing import CirclePacker

centers = CirclePacker.pack(polygon_vertices, radius=0.1)
```

**Mesh Voxelization:**
```python
from compgeom.mesh import MeshVoxelizer

# Using native surface sampling
voxels = MeshVoxelizer.voxelize_native(vertices, faces, voxel_size=0.1)
```

## Project Structure

- `src/compgeom/` - Core library modules:
    - `geometry.py`: Primitives and types (Point, Point3D).
    - `math_utils.py`: Low-level mathematical functions.
    - `shapes.py`: High-level shape classes.
    - `polygon_smoothing.py`: `PolygonalMeanCurvatureFlow` class.
    - `distance_map.py`: `DistanceMapSolver` class.
    - `points_sampling.py`: `PointSampler` class.
    - `sequences.py`: `DavenportSchinzel` class.
    - `space_filling_curves.py`: `SpaceFillingCurves` class.
    - `rectangle_packing.py`: `RectanglePacker` class.
    - `circle_packing.py`: `CirclePacker` class.
    - `mesh/`: Mesh sub-package:
        - `mesh.py`: Mesh classes and `MeshTopology` helper.
        - `mesh_io.py`: `OBJFileHandler` class.
        - `mesh_coloring.py`: `MeshColoring` class.
        - `mesh_refinement.py`: `TriMeshRefiner` class.
        - `mesh_reordering.py`: `CuthillMcKee` class.
        - `voxelization.py`: `MeshVoxelizer` class (Native & OpenVDB).
        - `triangulation.py`: Delaunay and Voronoi algorithms.
    - `spatial.py`: Spatial indexing and `PointSimplifier`.
    - `visualization.py`: SVG/PNG export utilities.
- `src/compgeom/cli/` - CLI script implementations.
- `tests/` - Comprehensive unit test suite.

## Development & Testing

To run the full test suite:

```bash
pytest tests
```

The repository is configured with GitHub Actions to run tests automatically on every push to `main`.
