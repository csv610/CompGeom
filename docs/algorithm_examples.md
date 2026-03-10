# Complete Python Examples

This guide collects complete Python examples for the algorithms called out in the main project overview. All examples use the current public API from `compgeom`.

## Foundations and Core Geometry

### Geometric predicates

```python
from compgeom import Point, incircle_sign, orientation_sign

a = Point(0.0, 0.0)
b = Point(2.0, 0.0)
c = Point(0.0, 2.0)
p = Point(0.5, 0.5)

turn = orientation_sign(a, b, c)
inside = incircle_sign(a, b, c, p)

print(turn)    # 1 means counter-clockwise
print(inside)  # 1 means inside the circumcircle
```

### Minimum enclosing shapes

```python
from compgeom import Point, minimum_bounding_box, minimum_enclosing_circle

points = [
    Point(0, 1),
    Point(1, 0),
    Point(0, -1),
    Point(-1, 0),
]

center, radius = minimum_enclosing_circle(points)
box = minimum_bounding_box(points)

print(center, radius)
print(box["width"], box["height"], box["area"])
```

## Polygon Processing

### Polygon properties and diameter

```python
from compgeom import Point, get_convex_diameter, get_polygon_properties

polygon = [
    Point(0, 0),
    Point(4, 0),
    Point(4, 3),
    Point(0, 3),
]

area, centroid, is_clockwise = get_polygon_properties(polygon)
diameter = get_convex_diameter(polygon)

print(area)
print(centroid)
print(is_clockwise)
print(diameter)
```

### Point in polygon and visibility polygon

```python
from compgeom import Point, is_point_in_polygon, visibility_polygon

polygon = [
    Point(0, 0),
    Point(5, 0),
    Point(5, 1),
    Point(2, 1),
    Point(2, 4),
    Point(5, 4),
    Point(5, 5),
    Point(0, 5),
]
query = Point(1, 2.5)

print(is_point_in_polygon(query, polygon))

visible = visibility_polygon(query, polygon)
for vertex in visible:
    print(vertex)
```

### Convex hull: Graham scan and monotone chain

```python
from compgeom import Point, graham_scan, monotone_chain

points = [
    Point(0, 0),
    Point(2, 0),
    Point(1, 1),
    Point(2, 2),
    Point(0, 2),
    Point(1, 0.5),
]

hull_a = graham_scan(points)
hull_b = monotone_chain(points)

print(hull_a)
print(hull_b)
```

### Spatial indexing: KD-tree range search, interval tree, and segment tree

```python
from compgeom import (
    Interval,
    IntervalTree,
    Point,
    SegmentTree,
    build_kdtree,
    range_search,
)

# Orthogonal range query on sampled geometry points.
points = [
    Point(0, 0),
    Point(2, 1),
    Point(3, 4),
    Point(5, 2),
    Point(6, 5),
]

root = build_kdtree(points)
hits = range_search(root, 1, 5, 1, 4)
print(hits)

# Active x-intervals from projected line segments in a sweep-line stage.
intervals = [
    Interval(0.0, 2.5, "segment_ab"),
    Interval(1.5, 4.0, "segment_cd"),
    Interval(3.0, 5.5, "segment_ef"),
]

interval_tree = IntervalTree(intervals)
print(interval_tree.query_point(2.0))
print(interval_tree.query_interval(2.0, 3.5))

# Occupancy counts across scanline buckets.
segment_tree = SegmentTree.for_sum([3, 1, 0, 2, 4, 1])
print(segment_tree.range_query(1, 4))
segment_tree.update(2, 5)
print(segment_tree.range_query(1, 4))
```

### Polygon generation

```python
from compgeom import PolygonGenerator

convex = PolygonGenerator.convex(n_points=8, x_range=(0, 10), y_range=(0, 10))
concave = PolygonGenerator.concave(n_points=8, x_range=(0, 10), y_range=(0, 10))
star = PolygonGenerator.star_shaped(n_points=10)

print(len(convex), len(concave), len(star))
```

### Polygon smoothing

```python
from compgeom import PolygonGenerator, PolygonalMeanCurvatureFlow

polygon = PolygonGenerator.concave(n_points=12, x_range=(0, 20), y_range=(0, 20))
resampled = PolygonalMeanCurvatureFlow.resample_polygon(polygon, n_points=60)
smoothed = PolygonalMeanCurvatureFlow.smooth(resampled, iterations=25, step_size=0.05)

print(len(resampled), len(smoothed))
```

### Concave part identification and convex decomposition

```python
from compgeom import Point, ConvexDecomposer, get_reflex_vertices, hertel_mehlhorn

polygon = [
    Point(0, 0),
    Point(6, 0),
    Point(6, 5),
    Point(3, 2),
    Point(0, 5),
]

reflex_vertices = get_reflex_vertices(polygon)
pieces_a = hertel_mehlhorn(polygon)
pieces_b = ConvexDecomposer.hertel_mehlhorn(polygon)

print(reflex_vertices)
print(len(pieces_a), len(pieces_b))
```

### Art gallery problem

```python
from compgeom import Point, solve_art_gallery

polygon = [
    Point(0, 0),
    Point(6, 0),
    Point(6, 5),
    Point(3, 2),
    Point(0, 5),
]

guards = solve_art_gallery(polygon)
print(guards)
```

### Polygon triangulation with holes

```python
from compgeom import Point, triangulate_polygon_with_holes

outer = [
    Point(0, 0),
    Point(6, 0),
    Point(6, 6),
    Point(0, 6),
]
holes = [[
    Point(2, 2),
    Point(4, 2),
    Point(4, 4),
    Point(2, 4),
]]

triangles, merged_boundary = triangulate_polygon_with_holes(outer, holes)

print(len(triangles))
print(len(merged_boundary))
```

### Shortest path inside a polygon

```python
from compgeom import Point, shortest_path_in_polygon

polygon = [
    Point(0, 0),
    Point(4, 0),
    Point(4, 4),
    Point(2, 2),
    Point(0, 4),
]

path, length = shortest_path_in_polygon(polygon, Point(1, 3), Point(3, 3))

print(path)
print(length)
```

### Circle packing

```python
from compgeom import CirclePacker, Point

polygon = [
    Point(0, 0),
    Point(10, 0),
    Point(10, 6),
    Point(0, 6),
]

centers = CirclePacker.pack(polygon, radius=0.75)
efficiency = CirclePacker.calculate_efficiency(polygon, centers, radius=0.75)

print(len(centers))
print(round(efficiency, 2))
```

### Distance maps

```python
from compgeom import DistanceMapSolver, Point

polygon = [
    Point(0, 0),
    Point(4, 0),
    Point(4, 3),
    Point(0, 3),
]

grid, extent = DistanceMapSolver.solve(polygon, resolution=30)
svg = DistanceMapSolver.visualize_svg(grid, extent)

print(len(grid), len(grid[0]))
print(extent)
print(svg[:80])
```

### Medial axis approximation

```python
from compgeom import Point, approximate_medial_axis

polygon = [
    Point(0, 0),
    Point(2, 0),
    Point(2, 2),
    Point(0, 2),
]

medial_axis = approximate_medial_axis(polygon, resolution=0.5)

print(len(medial_axis["samples"]))
print(len(medial_axis["centers"]))
print(len(medial_axis["segments"]))
```

### Planar subdivision with a DCEL

```python
from compgeom import Point, build_polygon_dcel, locate_face

dcel = build_polygon_dcel(
    [Point(0, 0), Point(6, 0), Point(6, 6), Point(0, 6)],
    holes=[[
        Point(2, 2),
        Point(4, 2),
        Point(4, 4),
        Point(2, 4),
    ]],
)

inside = locate_face(dcel, Point(1, 1))
hole = locate_face(dcel, Point(3, 3))
outside = locate_face(dcel, Point(7, 1))

print(len(dcel.vertices), len(dcel.half_edges), len(dcel.faces))
print(inside.is_exterior, hole.is_exterior, outside.is_exterior)
```

## Mesh Processing and Modeling

### Mesh topology and adjacency queries

```python
from compgeom import Point, TriangleMesh

vertices = [
    Point(0, 0, 0),
    Point(1, 0, 1),
    Point(0, 1, 2),
    Point(1, 1, 3),
]
faces = [(0, 1, 2), (1, 3, 2)]

mesh = TriangleMesh(vertices, faces)

print(mesh.topology.vertex_neighbors(1))
print(mesh.topology.shared_edge_neighbors(0))
print(mesh.topology.boundary_edges())
```

### Euler characteristic and standalone mesh-neighbor helpers

```python
from compgeom import Point, euler_characteristic, mesh_neighbors

triangles = [
    (Point(0, 0, 0), Point(1, 0, 1), Point(0, 1, 2)),
    (Point(1, 0, 1), Point(1, 1, 3), Point(0, 1, 2)),
]

neighbors = mesh_neighbors(triangles)
chi = euler_characteristic(triangles)

print(neighbors["vertex_neighbors"])
print(neighbors["triangle_neighbors"])
print(chi)
```

### Mesh refinement

```python
from compgeom import Point, TriMeshRefiner, TriangleMesh

mesh = TriangleMesh(
    [Point(0, 0, 0), Point(2, 0, 1), Point(0, 2, 2)],
    [(0, 1, 2)],
)

linear = TriMeshRefiner.subdivide_linear(mesh)
uniform = TriMeshRefiner.refine_uniform(mesh, max_area_ratio=0.2)

print(len(linear.vertices), len(linear.faces))
print(len(uniform.vertices), len(uniform.faces))
```

### Mesh reordering

```python
from compgeom import CuthillMcKee, Point, TriangleMesh

mesh = TriangleMesh(
    [
        Point(0, 0, 0),
        Point(1, 0, 1),
        Point(0, 1, 2),
        Point(1, 1, 3),
    ],
    [(0, 1, 2), (1, 3, 2)],
)

permutation = CuthillMcKee.reorder_vertices(mesh)
mesh.reorder_nodes(permutation)

print(permutation)
print(mesh.faces)
```

### Mesh coloring

```python
from compgeom import MeshColoring, Point, TriangleMesh

mesh = TriangleMesh(
    [
        Point(0, 0, 0),
        Point(1, 0, 1),
        Point(0, 1, 2),
        Point(1, 1, 3),
    ],
    [(0, 1, 2), (1, 3, 2)],
)

vertex_colors = MeshColoring.color_vertices(mesh)
element_colors = MeshColoring.color_elements(mesh)

print(vertex_colors)
print(element_colors)
```

### Triangle-to-quad conversion

```python
from compgeom import Point, TriangleMesh, TriangleToQuadConverter

mesh = TriangleMesh(
    [Point(0, 0, 0), Point(1, 0, 1), Point(0, 1, 2)],
    [(0, 1, 2)],
)

quad_mesh = TriangleToQuadConverter.convert(mesh)

print(len(quad_mesh.vertices))
print(quad_mesh.elements)
```

### Mesh topology transfer

```python
from compgeom import MeshTransfer, Point, TriangleMesh

source = TriangleMesh(
    [
        Point(0, 0, 0),
        Point(1, 0, 1),
        Point(1, 1, 2),
        Point(0, 1, 3),
    ],
    [(0, 1, 2), (0, 2, 3)],
)

target_boundary = [
    Point(0, 0),
    Point(2, 0),
    Point(2, 1),
    Point(1, 2),
    Point(0, 1),
]

transferred = MeshTransfer.transfer(source, target_boundary)

print(transferred.vertices)
print(transferred.faces)
```

### Delaunay triangulation, constrained Delaunay, and Voronoi cells

```python
from compgeom import (
    Point,
    constrained_delaunay_triangulation,
    get_square_boundary,
    get_voronoi_cells,
    triangulate,
)

points = [
    Point(0, 0, 0),
    Point(1, 0, 1),
    Point(0, 1, 2),
    Point(1, 1, 3),
]

triangles, skipped = triangulate(points)
cdt_triangles, constrained_edges = constrained_delaunay_triangulation(
    get_square_boundary(size=4, center=(2, 2))
)
voronoi = get_voronoi_cells(
    [Point(1, 1), Point(3, 1), Point(2, 3)],
    get_square_boundary(size=4, center=(2, 2)),
)

print(len(triangles), len(skipped))
print(len(cdt_triangles), len(constrained_edges))
print(len(voronoi))
```

### Dynamic Delaunay insertion

```python
from compgeom import DynamicDelaunay, Point

triangulation = DynamicDelaunay(width=10, height=10)
triangulation.add_point(Point(2, 2, 0))
triangulation.add_point(Point(8, 2, 1))
triangulation.add_point(Point(5, 8, 2))

print(len(triangulation.get_triangles()))
```

### Shortest path on a triangle mesh

```python
from compgeom import Point, shortest_path

triangles = [
    (Point(0, 0, 0), Point(1, 0, 1), Point(0, 1, 2)),
    (Point(1, 0, 1), Point(1, 1, 3), Point(0, 1, 2)),
]

path, length = shortest_path(triangles, Point(0, 0, 0), Point(1, 1, 3), mode="edges")

print(path)
print(length)
```

## Spatial Algorithms and Visualization

### Point sampling

```python
from compgeom import Point, Point3D, PointSampler

disk = PointSampler.in_circle(Point(0, 0), radius=2.0, n_points=5)
rectangle = PointSampler.in_rectangle(width=4.0, height=2.0, n_points=5)
triangle = PointSampler.in_triangle(Point(0, 0), Point(2, 0), Point(0, 2), n_points=5)
cube = PointSampler.in_cube(side_length=2.0, n_points=5, center=Point3D(0, 0, 0))
sphere = PointSampler.on_sphere(Point3D(0, 0, 0), radius=1.0, n_points=5)

print(disk)
print(rectangle)
print(triangle)
print(cube)
print(sphere)
```

### Point simplification

```python
from compgeom import Point, PointSimplifier

points = [Point(x / 10.0, y / 10.0, id=10 * x + y) for x in range(10) for y in range(10)]
simplified = PointSimplifier.simplify(points, ratio=0.15, protected_ids={0, 99})

print(len(points), len(simplified))
print(any(point.id == 0 for point in simplified))
print(any(point.id == 99 for point in simplified))
```

### Quadtrees and KD-trees

```python
from compgeom import Point, PointQuadtree, build_kdtree

points = [
    Point(0, 0),
    Point(2, 1),
    Point(-1, 3),
    Point(3, -2),
]

quadtree = PointQuadtree()
for point in points:
    quadtree.insert(point)

kdtree = build_kdtree(points)

print(quadtree.count)
print(kdtree.point)
```

### Closest pair, farthest pair, segment intersection, and Minkowski sum

```python
from compgeom import (
    Point,
    closest_pair,
    do_intersect,
    farthest_pair,
    minkowski_sum,
)

points = [Point(0, 0), Point(1, 0), Point(2, 0), Point(1, 2)]

distance, pair = closest_pair(points)
farthest = farthest_pair(points)
intersects = do_intersect(Point(0, 0), Point(2, 2), Point(0, 2), Point(2, 0))
sum_polygon = minkowski_sum(
    [Point(0, 0), Point(1, 0), Point(0, 1)],
    [Point(0, 0), Point(2, 0), Point(0, 2)],
)

print(distance, pair)
print(farthest)
print(intersects)
print(sum_polygon)
```

### Davenport-Schinzel lower envelope

```python
from compgeom import DavenportSchinzel, Point

segments = [
    (Point(0, 4), Point(4, 0)),
    (Point(0, 2), Point(4, 2)),
    (Point(0, 0), Point(4, 4)),
]

envelope = DavenportSchinzel.lower_envelope_segments(segments)
sequence = DavenportSchinzel.calculate_sequence(segments)

print(envelope)
print(sequence)
```

### Rectangle packing

```python
from compgeom import RectanglePacker

width, height, placements = RectanglePacker.pack(
    [(4, 2), (3, 2), (2, 2), (1, 4)],
    target_shape="square",
)

svg = RectanglePacker.visualize(width, height, placements)

print(width, height)
print(placements)
print(svg[:80])
```

### Space-filling curves

```python
from compgeom import SpaceFillingCurves

hilbert = SpaceFillingCurves.hilbert(order=2)
peano = SpaceFillingCurves.peano(level=2)
morton = SpaceFillingCurves.morton(level=2)
zigzag = SpaceFillingCurves.zigzag(width=4, height=3)
sweep = SpaceFillingCurves.sweep(width=4, height=3)

svg = SpaceFillingCurves.visualize(hilbert, width=4, height=4, cell_size=30)

print(hilbert)
print(peano[:10])
print(morton)
print(zigzag)
print(sweep)
print(svg[:80])
```

### Random walks and grid paths

```python
from compgeom import (
    RandomWalker,
    generate_spiral_path,
    generate_zigzag_path,
    simulate_random_walk_2d,
    simulate_random_walk_3d,
    simulate_saw_2d,
)

walk2d = simulate_random_walk_2d(10, 10, 5, 5, max_steps=25)
walk3d = simulate_random_walk_3d(6, 6, 6, 3, 3, 3, max_steps=25)
saw = simulate_saw_2d(5, 5, 2, 2)
zigzag = generate_zigzag_path(4, 3)
spiral = generate_spiral_path(5, 5)
direct = RandomWalker.simulate_2d(8, 8, 4, 4, max_steps=10)

print(walk2d)
print(walk3d)
print(saw["reason"], saw["steps"])
print(zigzag)
print(spiral)
print(direct)
```

### SVG generation and export

```python
from compgeom import SpaceFillingCurves, generate_svg_path, save_svg

indices = SpaceFillingCurves.sweep(width=4, height=3)
svg = generate_svg_path(indices, width=4, height=3, cell_size=32)

save_svg(svg, "sweep.svg")
print(svg[:80])
```
