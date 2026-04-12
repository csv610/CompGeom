# Computational Geometry CLI Tools

This directory contains a collection of command-line interface (CLI) tools for various computational geometry and mesh processing algorithms. All tools are designed as purely functional utilities that require user input (via files, arguments, or stdin).

## General Usage

You can run these tools directly as Python scripts or through the main entry point `compgeom.cli.main`.

```bash
# Using the main entry point
python -m compgeom.cli.main <command> [options]

# Example:
python -m compgeom.cli.main graham_scan --visualize < points.txt
```

### Common Input Formats

Many tools read points or polygons from standard input (stdin).
- **Points:** One point per line, specified as `x y` (or `id x y` if IDs are required).
- **Polygons:** A sequence of points (vertices) in order.
- **Multiple Polygons:** Separated by a line containing the keyword `NEXT`.

---

## Tool Index

### 1. `art_gallery_problem`
- **Objective:** Solve the Art Gallery Problem by placing a minimum number of guards to cover a polygon.
- **Parameters:**
  - `-i, --input <file>`: Path to input OFF file defining the polygon.
- **Expected Output:** Number of guards placed and their coordinates.
- **Common Errors:** Invalid OFF file format; self-intersecting polygon.

### 2. `circle_packing`
- **Objective:** Pack circles of a given radius into a closed polygon.
- **Parameters:**
  - `--input <file>`: Path to input OBJ file defining the container polygon.
  - `--poly <coords>`: Polygon vertices as `x1 y1 x2 y2 ...`.
  - `--radius <val>`: Radius of circles to pack (default: 0.5).
  - `--output <file>`: Visualization output (.png or .svg).
- **Expected Output:** Number of packed circles and their efficiency.
- **Common Errors:** Polygon not closed; radius too large for polygon.

### 3. `closest_pair`
- **Objective:** Find the closest pair of points in a 2D point set.
- **Parameters:** Reads points from stdin.
- **Expected Output:** Coordinates of the two closest points and the distance between them.
- **Common Errors:** Fewer than 2 points provided.

### 4. `convex_decomposition`
- **Objective:** Decompose a simple polygon into convex pieces using the Hertel-Mehlhorn algorithm.
- **Parameters:**
  - `--input <file>`: Input OBJ file.
  - `--poly <coords>`: Polygon vertices.
  - `--output <file>`: Visualization output.
- **Expected Output:** Number of convex pieces generated and vertex counts for each.
- **Common Errors:** Input polygon is not simple (self-intersects).

### 5. `constrained_tet_mesh`
- **Objective:** Generate a constrained tetrahedral mesh from a surface mesh.
- **Parameters:**
  - `input`: Path to input surface mesh file.
  - `output`: Path to output tetrahedral mesh file.
  - `--refine <float>`: Refinement factor for internal Steiner points (default: 1.0).
- **Expected Output:** Tetrahedral mesh with vertex and cell counts.

### 6. `constrained_tri_mesh`
- **Objective:** Compute Constrained Delaunay Triangulation (CDT) for a polygon with optional holes.
- **Parameters:**
  - Reads outer boundary and holes from stdin (separate holes with `HOLE` keyword).
  - `--visualize`: PyVista visualization.
- **Expected Output:** List of triangles in the CDT.

### 7. `convex_decomposition`
- **Objective:** Decompose a simple polygon into convex pieces using the Hertel-Mehlhorn algorithm.
- **Parameters:**
  - `--input <file>`: Input OBJ file.
  - `--poly <coords>`: Polygon vertices.
  - `--output <file>`: Visualization output.
- **Expected Output:** Number of convex pieces generated and vertex counts for each.
- **Common Errors:** Input polygon is not simple (self-intersects).

### 8. `convex_partition`
- **Objective:** Partition a polygon into a minimum number of convex parts.
- **Parameters:**
  - `-i, --input <file>`: Input OFF file.
- **Expected Output:** Coordinates of partitioned convex parts.

### 9. `convex_polygon_distance`
- **Objective:** Measure the minimum distance between two convex polygons.
- **Parameters:** Reads two polygons from stdin separated by a `NEXT` line.
- **Expected Output:** Minimum distance (0.0 if polygons overlap).
- **Common Errors:** Input polygons are not convex.

### 10. `davenport_schinzel`

### 11. `delaunay_flip`
- **Objective:** Convert an arbitrary triangulation into a Delaunay triangulation using edge flips.
- **Parameters:** Reads mesh data from stdin (points followed by 'T' and triangle indices).
- **Expected Output:** List of triangles in the final Delaunay triangulation.

### 12. `distance_map`
- **Objective:** Calculate a distance map (signed distance field) from polygon boundaries.
- **Parameters:**
  - `--input <file>`: Input OBJ file.
  - `--poly <coords>`: Polygon vertices.
  - `--res <int>`: Grid resolution (default: 100).
  - `--output <file>`: Visualization output.
- **Expected Output:** Grid dimensions and saved image.

### 13. `dynamic_delaunay`
- **Objective:** Build a Delaunay triangulation incrementally by inserting points.
- **Parameters:** Reads points from stdin.
- **Expected Output:** List of triangles in the final triangulation.

### 14. `euler_characteristic`
- **Objective:** Compute the Euler characteristic (V - E + F) for a 3D mesh.
- **Parameters:**
  - `input_file`: Path to mesh file (OBJ, OFF, STL, PLY).
- **Expected Output:** Count of vertices, edges, faces, and the Euler characteristic value.

### 15. `generate_circle_points`
- **Objective:** Generate random points uniformly sampled inside a circle.
- **Parameters:**
  - `--center <x y>`: Center of the circle.
  - `--radius <val>`: Circle radius (default: 2.5).
  - `--count <int>`: Number of points to generate (default: 100).
- **Expected Output:** List of generated point coordinates.

### 16. `generate_concave_shapes`
- **Objective:** Generate various types of random simple polygons.
- **Parameters:**
  - `type`: Type of polygon (`convex`, `concave`, `star`).
  - `--n <int>`: Number of vertices (default: 15).
  - `--output <file>`: Visualization output.
  - `--print`: Print vertices to stdout instead of visualizing.
- **Expected Output:** Coordinates or visualization of the generated polygon.

### 17. `generate_triangle_points`
- **Objective:** Generate random points uniformly sampled inside a triangle.
- **Parameters:**
  - Reads 3 vertices of the triangle from stdin.
  - `--count <int>`: Number of points to generate.
- **Expected Output:** List of generated point coordinates.

### 18. `geometric_predictes`
- **Objective:** Evaluate basic geometric predicates like orientation and incircle tests.
- **Parameters:**
  - `--points <coords>`: 8 coordinates for points A, B, C, and P.
- **Expected Output:** Orientation of (A, B, C) and containment of P in triangle/circle.

### 19. `graham_scan`
- **Objective:** Compute the convex hull of a 2D point set.
- **Parameters:**
  - Reads points from stdin.
  - `--visualize`: Show the result using PyVista.
- **Expected Output:** Vertices of the convex hull in CCW order.

### 20. `hilbert_walk2d`
- **Objective:** Generate and analyze a 2D Hilbert space-filling curve.
- **Parameters:**
  - `--order <int>`: Order of the Hilbert curve.
- **Expected Output:** Walk statistics including total steps and displacement.

### 21. `hopper`
- **Objective:** Discover new polytopes with specific properties using an AI-assisted search.
- **Parameters:**
  - `--dim <int>`: Dimension of the polytope.
  - `--points <int>`: Number of initial points.
  - `--iters <int>`: Number of iterations.
  - `--scenario <hirsch|neighborly>`: Search scenario.
- **Expected Output:** Best fitness achieved and polytope statistics.

### 22. `identify_concave_parts`
- **Objective:** Identify reflex vertices forming concave parts of a polygon.
- **Parameters:**
  - `--input <file>` / `--poly <coords>` / stdin input.
  - `--output <file>`: Visualization output.
- **Expected Output:** List of reflex vertices and their indices.

### 23. `largest_empty_circle`
- **Objective:** Find the largest empty circle within the convex hull of a point set.
- **Parameters:**
  - `--points <coords>` / stdin input.
  - `--output <file>`: Visualization output.
- **Expected Output:** Center and radius of the largest empty circle.

### 24. `line_arrangement`
- **Objective:** Analyze an arrangement of line segments, finding intersections and faces.
- **Parameters:** Reads segments (`x1 y1 x2 y2`) from stdin.
- **Expected Output:** Intersection points, split segments, and discovered polygons (faces).

### 25. `medial_axis_polygon`
- **Objective:** Approximate the medial axis of a simple polygon.
- **Parameters:**
  - Reads polygon from stdin.
  - `--resolution <val>`: Boundary sampling resolution.
- **Expected Output:** Medial axis nodes and segments.

### 26. `mesh_convert`
- **Objective:** Convert between different 3D mesh formats (OBJ, OFF, STL, PLY).
- **Parameters:**
  - `input`: Input mesh file path.
  - `output`: Output mesh file path (format determined by extension).
  - `--binary`: Write binary format if supported (STL, PLY).
- **Expected Output:** Confirmation of successful conversion.

### 27. `mesh_coloring`
- **Objective:** Apply greedy coloring to mesh elements (faces) or vertices.
- **Parameters:**
  - `--input <file>`: Input OBJ file.
  - `--target <elements|vertices>`: What to color.
- **Expected Output:** Number of colors used and mapping of indices to color IDs.

### 28. `mesh_info`
- **Objective:** Provide detailed information about a 3D or 2D mesh (nodes, edges, faces, bounding boxes, area, volume).
- **Parameters:**
  - `input`: Path to the input mesh file (OBJ, OFF, STL, PLY).
- **Expected Output:** Topological counts, centroid, AABB, OBB (2D only), surface area, volume, and connectivity checks (watertight/orientable).

### 29. `mesh_neighbors`
- **Objective:** Inspect adjacency relationships (vertex and triangle neighbors) in a mesh.
- **Parameters:** Reads mesh and queries (`P id` or `F id`) from stdin.
- **Expected Output:** List of neighbor indices for requested vertices/faces.

### 30. `mesh_refinement`
- **Objective:** Refine a triangular mesh using linear subdivision or area-based refinement.
- **Parameters:**
  - `--input <file>`: Input OBJ file.
  - `--iterations <int>`: Subdivision iterations.
  - `--max_area <val>`: Maximum allowed triangle area ratio.
  - `--output <file>`: Refined OBJ file.
- **Expected Output:** Final vertex and face counts.

### 31. `mesh_reordering`
- **Objective:** Reorder mesh elements or vertices using the Cuthill-McKee algorithm to reduce bandwidth.
- **Parameters:**
  - `--input <file>`: Input OBJ file.
  - `--target <elements|vertices>`: What to reorder.
  - `--no_reverse`: Use CM instead of Reverse CM.
- **Expected Output:** Initial and final bandwidth, and reduction achieved.

### 32. `mesh_transfer`
- **Objective:** Transfer mesh topology from a source domain to a new polygonal boundary.
- **Parameters:**
  - `--input <file>`: Source OBJ file.
  - `--target <coords>`: Target polygon vertices.
  - `--output <file>`: Output OBJ file.
- **Expected Output:** Confirmation of successful transfer.

### 33. `mesh_voxelization`
- **Objective:** Convert a 3D surface mesh into a voxel grid.
- **Parameters:**
  - `--input <file>`: Input OBJ file.
  - `--voxel_size <val>`: Size of each voxel.
  - `--method <auto|native|openvdb>`: Voxelization backend.
  - `--fill`: Fill interior voxels.
- **Expected Output:** Number of voxels generated.

### 34. `minimum_bounding_shapes`
- **Objective:** Compute the minimum enclosing circle and minimum bounding box for a point set.
- **Parameters:** Reads points from stdin.
- **Expected Output:** Circle (center, radius) and Box (center, dimensions, corners, area).

### 35. `minkowski_sum`
- **Objective:** Compute the Minkowski sum of two polygons.
- **Parameters:** Reads two polygons from stdin separated by `NEXT`.
  - `--visualize`: PyVista visualization.
- **Expected Output:** Vertices of the resulting Minkowski sum polygon.

### 36. `morton_walk2d`
- **Objective:** Generate a 2D Morton (Z-order) space-filling curve.
- **Parameters:**
  - `--width`, `--height`: Grid dimensions.
- **Expected Output:** Walk statistics.

### 37. `peano_walk2d`
- **Objective:** Generate a 2D Peano space-filling curve.
- **Parameters:**
  - `--level <int>`: Curve recursion level.
- **Expected Output:** Walk statistics.

### 38. `point_in_polygon`
- **Objective:** Test if a query point is inside a given polygon.
- **Parameters:**
  - `--point <x y>`: Query point coordinates.
  - Reads polygon from stdin.
- **Expected Output:** `INSIDE` or `OUTSIDE` result.

### 39. `point_kdtree2d` / `point_quadtree2d`
- **Objective:** Build and display spatial index structures (KD-tree or Quadtree).
- **Parameters:** Reads points from stdin.
- **Expected Output:** Tree structure printed to stdout.

### 40. `point_simplification`
- **Objective:** Simplify a large point set using grid-based decimation.
- **Parameters:**
  - Reads points from stdin.
  - `--ratio <val>`: Simplification tolerance.
- **Expected Output:** Reduction percentage and timing.

### 41. `polygon_boolean_operations`
- **Objective:** Perform Union, Intersection, Difference, or XOR on two polygons.
- **Parameters:**
  - `--operation <op>`: The boolean operation.
  - Reads two polygons from stdin separated by `NEXT`.
- **Expected Output:** Resulting regions and their boundaries (with holes).

### 42. `polygon_properties`
- **Objective:** Compute basic properties (Area, Centroid, Orientation) of a polygon.
- **Parameters:** Reads polygon from stdin.
- **Expected Output:** Area, Centroid coordinates, and Orientation (CW/CCW).

### 43. `polygon_visibility`
- **Objective:** Compute visible boundary segments of a polygon from a given viewpoint.
- **Parameters:**
  - `--query <x y>`: Viewpoint coordinates.
  - Reads polygon from stdin.
- **Expected Output:** List of visible segments.

### 44. `polygonal_mean_curvature_flow`
- **Objective:** Smooth a polygon boundary using mean curvature flow.
- **Parameters:**
  - `--input <file>` / `--poly <coords>` / stdin.
  - `--iterations <int>`, `--dt <float>`: Flow parameters.
  - `--output <file>`: Visualization output.
- **Expected Output:** Confirmation of smoothing and saved image.

### 45. `rectangle_packer`
- **Objective:** Pack multiple rectangles into a minimum area container.
- **Parameters:**
  - `--dims <w1 h1 w2 h2 ...>`: Dimensions of rectangles.
  - `--shape <rectangle|square>`: Target container shape.
- **Expected Output:** Container size, packing efficiency, and individual placements.

### 46. `reflection_polygon`
- **Objective:** Animate a ray reflecting off the interior boundaries of a polygon.
- **Parameters:**
  - `--origin <x y>`: Ray starting point.
  - `--direction <dx dy>`: Ray direction vector.
  - Reads polygon from stdin.
- **Expected Output:** Interactive Tkinter window showing the reflection.

### 47. `rotating_calipers`
- **Objective:** Find the farthest pair of points (diameter) using the rotating calipers algorithm.
- **Parameters:** Reads points from stdin.
- **Expected Output:** The two points and the maximum distance.

### 48. `segment_intersection`
- **Objective:** Test if two line segments intersect.
- **Parameters:** Reads 4 points from stdin (forming two segments).
- **Expected Output:** `True` or `False`.

### 49. `self_avoiding_walk2d`
- **Objective:** Simulate a 2D self-avoiding walk on a grid.
- **Parameters:**
  - `--width`, `--height`: Grid dimensions.
- **Expected Output:** Reason for termination, steps taken, and final displacement.

### 50. `shortest_path_mesh`
- **Objective:** Compute the shortest path between two points across a mesh surface.
- **Parameters:** Reads mesh vertices, 'T' indices, and 'Q' source/target points from stdin.
- **Expected Output:** Path length and list of vertices along the path.

### 51. `simple_tri2quads`
- **Objective:** Convert a triangle mesh to a quad-dominant mesh using 1-to-3 splitting.
- **Parameters:**
  - `input`: Source triangle mesh (OBJ).
  - `output`: Resulting quad mesh (OBJ).
- **Expected Output:** Conversion statistics.

### 52. `spiral_walk2d` / `zigzag_walk2d`
- **Objective:** Generate grid traversal paths (Spiral or Zigzag).
- **Parameters:**
  - `--width`, `--height`: Grid dimensions.
- **Expected Output:** Path statistics.

### 53. `viewmesh`
- **Objective:** Interactively visualize a 3D mesh file.
- **Parameters:**
  - `file`: Path to the mesh file.
  - `--edges`, `--nodes`: Toggle display of edges/vertices.
- **Expected Output:** Interactive PyVista 3D viewer.

### 54. `visualize_curve`
- **Objective:** Generate an SVG visualization of various space-filling curves.
- **Parameters:**
  - `curve`: Type (`hilbert`, `peano`, `morton`, `zigzag`, `sweep`).
  - `--level <int>`: Recursion level.
  - `--output <file>`: Output SVG filename.
- **Expected Output:** Saved SVG file.

### 55. `voronoi_diagram`
- **Objective:** Generate a Voronoi diagram for a 2D point set.
- **Parameters:**
  - Reads points from stdin.
  - `--boundary-type <type>`: Type of boundary box.
  - `--visualize`: Show the result using PyVista.
- **Expected Output:** Vertices for each Voronoi cell.
