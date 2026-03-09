# CompGeom (Computational Geometry)

A comprehensive Python library and command-line tool for computational geometry, mesh operations, spatial algorithms, and visualizations.

## Features

- **Core Geometry:** Points (2D and 3D), vectors, primitive intersections, geometric predicates (orientation, incircle).
- **Mathematical Utilities:** High-precision orientation and incircle tests, coordinate conversions for space-filling curves, 2D/3D distances, and 2D rotations.
- **Polygons:** Boolean operations, properties (area, centroid, orientation), visibility, triangulation (ear-clipping, CDT), and shortest paths.
- **Proximity & Bounding:** Closest/farthest pair, Graham scan, monotone chain, minimum bounding box, and minimum enclosing circle (Welzl's algorithm).
- **Space-Filling Curves:** Hilbert, Peano, Morton (Z-order), ZigZag, and Sweep curves with grid cell index output.
- **Point Sampling:** Uniform sampling from circles, rectangles, triangles, line segments, cubes, and spheres.
- **Point Cloud Simplification:** $O(N)$ high-performance grid decimation (Voxel Grid) for simplifying massive datasets (millions/billions of points) based on spatial density.
- **Rectangle Packing:** Area-minimized packing into rectangular or square containers with efficiency reporting.
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
    - `space_filling_curves.py`: `SpaceFillingCurves` class.
    - `rectangle_packing.py`: `RectanglePacker` class.
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
