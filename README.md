# CompGeom (Computational Geometry)

A comprehensive Python library and command-line tool for computational geometry, mesh operations, spatial algorithms, and visualizations.

## Features

- **Core Geometry:** Points (2D and 3D), vectors, primitive intersections, geometric predicates (orientation, incircle).
- **Mathematical Utilities:** High-precision orientation and incircle tests, coordinate conversions for space-filling curves, 2D/3D distances, and 2D rotations.
- **Polygons:** Boolean operations, properties (area, centroid, orientation), visibility, triangulation (ear-clipping, CDT), and shortest paths.
- **Proximity & Bounding:** Closest/farthest pair, Graham scan, monotone chain, minimum bounding box, and minimum enclosing circle (Welzl's algorithm).
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

**Simplify a Large Point Cloud:**
```bash
# Simplify 1 million points with a 0.001 diagonal ratio in 3D
compgeom point_simplification --n 1000000 --ratio 0.001 --dim 3d
```

**Visualize a Space-Filling Curve:**
```bash
compgeom visualize_curve hilbert --level 3 --output path.png
```

**Pack Rectangles into a Square:**
```bash
compgeom rectangle_packer --dims 10 10 20 5 5 15 --shape square --output packed.png
```

### Python API

You can use the high-level classes directly in your Python code:

**Circle Packing (into a Square or Circle):**
```python
import math
from compgeom.geometry import Point
from compgeom.circle_packing import CirclePacker

# 1. Packing into a Square
square = [Point(0, 0), Point(10, 0), Point(10, 10), Point(0, 10)]
centers = CirclePacker.pack(square, radius=0.1)
efficiency = CirclePacker.calculate_efficiency(square, centers, radius=0.1)

# 2. Packing into a Circle (approximated as a high-res polygon)
container_radius = 10.0
polygon = [
    Point(container_radius * math.cos(2 * math.pi * i / 128),
          container_radius * math.sin(2 * math.pi * i / 128))
    for i in range(128)
]
centers_in_circle = CirclePacker.pack(polygon, radius=0.1)
```

**Mesh Voxelization:**
```python
from compgeom.voxelization import MeshVoxelizer

# Using native surface sampling
voxels = MeshVoxelizer.voxelize_native(vertices, faces, voxel_size=0.1)

# Using OpenVDB (requires pyopenvdb)
grid = MeshVoxelizer.voxelize_openvdb(vertices, faces, voxel_size=0.1)
```

**Point Cloud Simplification:**
```python
from compgeom.spatial import PointSimplifier
from compgeom.geometry import Point3D

# Simplify a list of 3D points
# Ratio is relative to the bounding box diagonal
simplified = PointSimplifier.simplify(my_large_point_list, ratio=0.005)
```

**Point Sampling:**
```python
from compgeom.geometry import Point
from compgeom.points_sampling import PointSampler

# Sample 50 points from a circle
points = PointSampler.in_circle(Point(0, 0), radius=10.0, n_points=50)
```

**Rectangle Packing:**
```python
from compgeom.rectangle_packing import RectanglePacker

dims = [(10, 20), (5, 5), (15, 10)]
w, h, placements = RectanglePacker.pack(dims, target_shape="square")
print(f"Packed into {w}x{h} container")
```

## Project Structure

- `src/compgeom/` - Core library modules:
    - `geometry.py`: Primitives and types (Point, Point3D).
    - `math_utils.py`: Low-level mathematical functions.
    - `points_sampling.py`: `PointSampler` class.
    - `sequences.py`: `DavenportSchinzel` class.
    - `space_filling_curves.py`: `SpaceFillingCurves` class.
    - `rectangle_packing.py`: `RectanglePacker` class.
    - `circle_packing.py`: `CirclePacker` class.
    - `mesh_io.py`: `OBJFileHandler` class.
    - `voxelization.py`: `MeshVoxelizer` class (Native & OpenVDB).
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
