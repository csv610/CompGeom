# CGAL companion examples

This directory contains small, complete C++ programs corresponding to the
book's core algorithms. They use CGAL kernels and predicates directly so that
the examples demonstrate the difference between a geometric algorithm and a
robust implementation of it.

The examples currently cover:

- convex_hull: planar convex hull construction;
- segment_intersection: point, segment-overlap, and disjoint cases;
- delaunay_triangulation: Delaunay construction and Voronoi dual output;
- polygon_boolean: exact polygon intersection and area verification;
- arrangement_point_location: arrangement construction and point location.
- convex_hull: file-driven 2D/3D hulls;
- verify_convex_hull: dimension-independent hull verification;
- verify_voronoi: dimension-independent Voronoi/Delaunay verification;
- verify_delaunay: dimension-independent Delaunay mesh verification;
- benchmark_convex_hull: 2D/3D hull benchmark for 10 through 1,000,000 points;
- benchmark_delaunay_mesh: 2D/3D Delaunay mesh benchmark for the same sizes;
- benchmark_voronoi: 2D/3D Voronoi benchmark for the same sizes;
- delaunay_mesher: file-driven 2D/3D Delaunay meshes;
- voronoi: file-driven 2D/3D Voronoi dual statistics.
- constrained_delaunay_mesh: constrained 2D/3D mesh construction.
- constrained_voronoi: constrained 2D/3D Voronoi dual construction.
- generate_points: random point-file generation in square, rectangle, box,
  cube, or sphere domains.

`segment_intersection` reads one segment per line and detects the dimension:

~~~
# optional segment count
2
0 0 4 4
0 4 4 0
~~~

Use `x1 y1 x2 y2` for 2D or `x1 y1 z1 x2 y2 z2` for 3D segments. It tests
every pair and reports disjoint, point, or overlapping-segment intersections.

## Point files

The large-input programs read whitespace-separated coordinates. A leading
single integer count is optional, and lines beginning with `#` are ignored:

~~~
# optional count
4
0 0
1 0
1 1
0 1
~~~

The point readers automatically detect `.obj` and `.off` files. OBJ vertex
records use `v x y z`; OFF files contain an `OFF` header and vertex records.
For 2D points, OBJ/OFF uses `z=0`. The legacy whitespace format remains
accepted for compatibility. Use two coordinates for 2D text files and three
coordinates for 3D text files. The
programs report counts and timing rather than printing the generated
million-point structures. `delaunay_mesher points.txt max_edge`
enables quality refinement; omitting `max_edge` only builds the input
triangulation, which is the practical default for already dense million-point
datasets. The 3D program constructs the Delaunay tetrahedral mesh from the
input sites; CGAL's full 3D quality mesher additionally requires a domain
description (for example, a polyhedron or implicit function).

Generate input files with the Python `argparse` command:

~~~
python3 generate_points.py --domain square --count 1000000 --output square.off --format off --side 100
python3 generate_points.py --domain rectangle --count 1000000 --output rectangle.obj --format obj --width 200 --height 100
python3 generate_points.py --domain box --count 1000000 --output box.off --format off --width 100 --height 100 --depth 50
python3 generate_points.py --domain cube --count 1000000 --output cube.obj --format obj --side 100
python3 generate_points.py --domain sphere --count 1000000 --output sphere.off --format off --radius 50
~~~

Square and rectangle generate 2D points. Box, cube, and sphere generate 3D
points. Sphere samples uniformly inside the sphere, not only on its surface.

## Constrained Delaunay mesh

For 2D, provide one constraint segment per line:

~~~
4
0 0 10 0
10 0 10 10
10 10 0 10
0 10 0 0
~~~

Run:

~~~
./build/constrained_delaunay_mesh --dimension 2 constraints.txt
~~~

For 3D, provide a closed triangular OBJ or OFF surface:

~~~
./build/constrained_delaunay_mesh --dimension 3 domain.off
~~~

The 2D path preserves input constraints during Delaunay refinement. The 3D
path uses the input surface as a CGAL Mesh_3 domain and generates constrained
tetrahedra inside it.

## Constrained Voronoi diagram

Use the same constraint files as `constrained_delaunay_mesh`:

~~~
./build/constrained_voronoi --dimension 2 constraints.txt
./build/constrained_voronoi --dimension 3 domain.off
~~~

The 2D result is the dual of the constrained Delaunay triangulation. In 3D,
the closed OBJ/OFF surface defines the domain, and the program reports the
Voronoi dual segments whose midpoints lie inside that domain, together with
boundary rays and lines.

## Build

Install CGAL, GMP, and Boost using the platform's package manager. Then:

~~~
cmake -S book/cgal_codes -B book/cgal_codes/build -DCMAKE_BUILD_TYPE=Release
cmake --build book/cgal_codes/build --parallel
~~~

Run an example from the repository root:

~~~
./book/cgal_codes/build/convex_hull points.off
./book/cgal_codes/build/delaunay_triangulation points_2d.txt
~~~

`convex_hull` is dimension-independent: it reads one file, detects 2D versus
3D coordinates, and dispatches internally to CGAL's `convex_hull_2` or
`convex_hull_3`. OBJ/OFF files whose vertices all have `z=0` are treated as
2D; any nonzero `z` coordinate selects the 3D algorithm.

Verify a point set with:

~~~
./build/verify_convex_hull points.off
~~~

The verifier computes the appropriate hull and checks that every input point
is inside or on its boundary. It returns exit code `0` when valid.

Verify a Voronoi diagram with:

~~~
./build/verify_voronoi points.off
~~~

This checks CGAL's Delaunay triangulation and confirms that every finite
Delaunay edge (2D) or facet (3D) has a valid Voronoi dual object.

Verify a Delaunay mesh with:

~~~
./build/verify_delaunay points.off
~~~

The verifier runs CGAL's internal validity and Delaunay checks for the
dimension detected from the input file.

Benchmark convex hull performance:

~~~
./build/benchmark_convex_hull --dimension 2 --seed 42 > hull_2d.csv
./build/benchmark_convex_hull --dimension 3 --seed 42 > hull_3d.csv
~~~

Each run uses the fixed sizes 10, 100, 1,000, 10,000, 100,000, and 1,000,000
and writes CSV timing results. The one-million-point 3D case can require
substantial memory.

Benchmark Delaunay mesh construction:

~~~
./build/benchmark_delaunay_mesh --dimension 2 --seed 42 > delaunay_2d.csv
./build/benchmark_delaunay_mesh --dimension 3 --seed 42 > delaunay_3d.csv
~~~

The default measures Delaunay construction. Optional 2D quality refinement
can be enabled with `--refine-max-edge value`; this is not recommended for the
million-point case unless sufficient memory is available.

Benchmark Voronoi dual construction:

~~~
./build/benchmark_voronoi --dimension 2 --seed 42 > voronoi_2d.csv
./build/benchmark_voronoi --dimension 3 --seed 42 > voronoi_3d.csv
~~~

The Voronoi diagram is represented through CGAL's Delaunay duals; the CSV
contains the number of finite Delaunay edges/facets and the resulting dual
segments, rays, and lines.

CGAL is intentionally a required CMake dependency. If it is not installed,
configuration stops with a clear error instead of silently compiling a
non-robust replacement. The programs use
Exact_predicates_inexact_constructions_kernel where coordinates are input
doubles and exact predicates are needed; the polygon Boolean and arrangement
examples use Exact_predicates_exact_constructions_kernel because exact
output coordinates are part of the demonstration.

The generated build/ directory is ignored locally and should not be
committed. For reproducible reports, record the CGAL version, compiler,
kernel choice, input data, and build type.
