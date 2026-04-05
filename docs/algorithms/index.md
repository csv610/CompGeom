# CompGeom Algorithms Index

This directory contains detailed documentation for the algorithms implemented in the `CompGeom` library. Each entry provides a comprehensive overview, theoretical background, and implementation details.

### Convex Hull & Partitioning
- [Chan's Algorithm](chans_algorithm.md) - Output-sensitive $O(n \log h)$ convex hull.
- [Graham Scan](graham_scan.md) - Classic $O(n \log n)$ sorting-based convex hull.
- [Monotone Chain](monotone_chain.md) - Efficient $O(n \log n)$ upper/lower chain hull.
- [QuickHull](quickhull.md) - Divide and conquer convex hull.
- [Convex Hull Peeling](convex_hull_peeling.md) - Recursive onion layers of a point set.
- [Convex Decomposition](convex_decomposition.md) - Partitioning concave polygons into convex parts.
- [Convex Partitioning](convex_partitioning.md) - Optimal decomposition into minimum convex parts.

### Triangulation & Diagrams
- [Ear Clipping](ear_clipping.md) - Simple polygon triangulation.
- [Monotone Decomposition](monotone_decomposition.md) - Splitting polygons into monotone pieces for triangulation.
- [Incremental Delaunay Triangulation](incremental_delaunay.md) - Stateful Delaunay construction.
- [Dynamic Delaunay](dynamic_delaunay.md) - Maintaining Delaunay with point insertion/deletion.
- [Delaunay Flips](delaunay_flips.md) - Local edge flipping to restore Delaunay property.
- [Voronoi Diagram](voronoi_diagram.md) - Dual of the Delaunay triangulation.
- [Kinetic Voronoi](kinetic_voronoi.md) - Voronoi diagrams for moving points.

### Proximity & Searching
- [Closest Pair of Points](closest_pair.md) - Finding the two nearest points in a set.
- [Nearest Neighbor & Proximity](proximity_queries.md) - General proximity and distance queries.
- [Range Search](range_search.md) - Efficient retrieval of objects within a region.
- [Point in Polygon](point_in_polygon_winding.md) - Determining if a point is inside a polygon.
- [Largest Empty Circle](largest_empty_circle.md) - Max radius circle within a point set.
- [Minimum Bounding Boxes](minimum_bounding_boxes.md) - Smallest area rectangle enclosing points.
- [Maximum Overlap](maximum_overlap.md) - Finding regions with the most overlapping objects.

### Spatial Data Structures
- [KD-Tree](kd_tree.md) - Multidimensional binary search tree.
- [Quadtree](quadtree.md) - 2D recursive space partitioning.
- [R-Tree](r_tree.md) - Hierarchical bounding box indexing.
- [Interval Tree](interval_tree.md) - 1D range searching for segments.
- [Segment Tree](segment_tree.md) - Array-based range query structure.

### Mesh Analysis & Processing
- [Mesh Connected Components](mesh_connected_components.md) - Identifying disjoint mesh parts.
- [Mesh Boundary Detection](mesh_boundary_detection.md) - Finding perimeter and hole loops.
- [Mesh Orientability](mesh_orientability.md) - Checking for consistent surface normals.
- [Manifold Verification](manifold_verification.md) - Checking topological validity.
- [Euler Characteristic](euler_characteristic.md) - Global topological invariant ($V-E+F$).
- [Node Degree (Valence)](node_degree.md) - Connectivity analysis per vertex.
- [Mesh Coloring](mesh_coloring.md) - Independent sets for parallel processing.
- [Mesh Reordering](mesh_reordering.md) - Bandwidth reduction for sparse solvers.
- [Mesh Rigidity](mesh_rigidity.md) - Analyzing structural stability of frameworks.

### Surface Geometry & Parameterization
- [BFF Parameterization](bff_parameterization.md) - Boundary First Flattening for conformal mapping.
- [Harmonic Mapping](harmonic_mapping.md) - Topology transfer and parameterization.
- [Functional Maps](functional_maps.md) - Spectral shape matching.
- [Mean Curvature Flow](mean_curvature_flow.md) - Surface smoothing via diffusion.
- [Affine Heat Flow](affine_heat_flow.md) - Invariant polygon smoothing.
- [Geodesic Distance](geodesic_distance.md) - Shortest paths on continuous surfaces.
- [Medial Axis Transform](medial_axis.md) - Shape skeletonization using Voronoi.
- [Straight Skeleton](straight_skeleton.md) - Linear skeleton via wavefront propagation.
- [Mesh Cut Loops](mesh_cut_loops.md) - Cutting a surface into a topological disk.
- [Mesh Tunnel Loops](mesh_tunnel_loops.md) - Identifying handles and homology basis.

### Discrete Exterior Calculus (DEC)
- [Hodge Star Computation](hodge_star.md) - Primal-dual mapping and metric weights.
- [Exterior Derivative](exterior_derivative.md) - Discrete Gradient and Curl operators.
- [Hodge Decomposition](hodge_decomposition.md) - Vector field decomposition (exact, co-exact, harmonic).
- [Discrete Morse Theory](discrete_morse_theory.md) - Topological simplification and feature extraction.

### Surface Modeling & Voxelization
- [Bézier Surface](bezier_surface.md) - Tensor product surface evaluation.
- [NURBS Surface](nurbs_surface.md) - Rational B-spline surface evaluation.
- [Mesh Voxelization](mesh_voxelization.md) - Volume conversion from surface meshes.
- [Mesh Refinement](mesh_refinement.md) - Subdivision and adaptive splitting.
- [CoACD](coacd.md) - Approximate convex decomposition for collision shapes.
- [Triangle to Quad](triangle_to_quad.md) - Converting triangle meshes to quad-dominant ones.

### Low-Discrepancy & Sampling
- [Poisson Disk Sampling](poisson_disk_sampling.md) - Blue noise point distribution.
- [Halton Points](halton_points.md) - Low-discrepancy quasi-random sequences.
- [Random Walk](random_walk.md) - Stochastic paths on meshes and grids.
- [Self-Avoiding Walk](self_avoiding_walk.md) - Paths that never intersect themselves.

### Space-Filling Curves
- [Hilbert Curve](hilbert_curve.md) - Fractal locality-preserving curve.
- [Morton Curve (Z-Order)](morton_curve.md) - Bit-interleaving spatial index.
- [Peano Curve](peano_curve.md) - Base-3 space-filling curve.
- [Zigzag Curve (Snake)](zigzag_curve.md) - Row-major and diagonal scanning.
- [Spiral Walk](spiral_walk.md) - Expanding traversal from a center point.

### Computational Algebra & Similarity
- [Buchberger's Algorithm](buchbergers_algorithm.md) - Gröbner basis computation.
- [Resultant-based Elimination](resultant_elimination.md) - Symbolic variable elimination.
- [Polygon Matching](polygon_matching.md) - Congruence and similarity testing.
- [Polygon Symmetry](polygon_symmetry.md) - Rotational and axial symmetry detection.

### Optimization & Distance
- [Circle Packing](circle_packing.md) - Optimal placement of non-overlapping disks.
- [Rectangle Packing](rectangle_packing.md) - 2D bin packing and sprite sheets.
- [Hopper Optimization](hopper_optimization.md) - Nesting of irregular non-convex shapes.
- [Fréchet Distance](frechet_distance.md) - Curve similarity (dog-leash metric).
- [Convex Polygon Distance](convex_polygon_distance.md) - Minimum distance between convex shapes.
- [Minkowski Sums](minkowski_sums.md) - Polygon addition for motion planning.
- [Welzl's Algorithm](welzls_algorithm.md) - Smallest enclosing circle in $O(n)$.
- [Davenport-Schinzel Sequences](davenport_schinzel.md) - Combinatorial complexity of lower envelopes.
- [Lower Envelopes](lower_envelopes.md) - Pointwise minimum of function sets.
- [Union Volume Estimation](union_volume_estimation.md) - Calculating area/volume of merged shapes.

### Other Operations
- [Polygon Boolean Operations](polygon_boolean.md) - Union, Intersection, Difference.
- [Line Arrangements](line_arrangements.md) - Subdivision of the plane by lines.
- [Art Gallery Guards](art_gallery_guards.md) - Optimal guard placement in polygons.
- [Fast Marching Method](fast_marching_method.md) - Solving Eikonal equations for distance maps.
- [Distance Map](distance_map.md) - Euclidean distance transforms on grids.
- [Dijkstra's Algorithm](dijkstra.md) - Shortest paths on discrete graphs.
- [Stochastic PDE](stochastic_pde.md) - Random fields and noise on meshes.
- [Wave Kernel Signature](wave_kernel.md) - Spectral geometric descriptors.
- [K-Geodesics](k_geodesics.md) - Intrinsic K-means clustering on surfaces.
- [Segment Intersection](segment_intersection.md) - Bentley-Ottmann sweep-line algorithm.
- [Point Simplification](voxel_grid_decimation.md) - Reducing point cloud density.
