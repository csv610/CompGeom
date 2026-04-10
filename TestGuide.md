# Geometric Algorithms Testing Guide

This document outlines the testing strategies, degenerate cases, and common failure modes for **every** geometric algorithm implemented in this codebase.

---

## 1. Geometric Predicates (Orientation, Incircle)

### (1) Testing Methods
- **Consistency Checks:** Verify that `orientation(a, b, c) == -orientation(b, a, c)`.
- **Known Results:** Test with axis-aligned points where the result is trivial.
- **Scaling Invariance:** Ensure `orientation(a, b, c) == orientation(k*a, k*b, k*c)` for $k > 0$.
- **Perturbation Testing:** Shift points by very small epsilon and check if the sign remains stable (or flips as expected).

### (2) Degenerate Cases
- **Collinear Points:** Three points lying on a perfectly straight line.
- **Duplicate Points:** Two or more points sharing the exact same coordinates.
- **Nearly Collinear:** Points that are collinear within floating-point precision but not bitwise identical.
- **Co-circular Points:** Four points exactly on the boundary of a circle (for Incircle).

---

## 2. Convex Hulls & Bounding Shapes

**Algorithms:** Graham Scan, Minimum Bounding Shapes (Box), Rotating Calipers, Smallest Enclosing Circle (Welzl's).

### (1) Testing Methods
- **Inclusion Test:** Every input point must be strictly inside or on the boundary of the hull/shape.
- **Convexity Test:** Every internal angle of a hull must be $\leq 180^\circ$.
- **Minimality:** For enclosing circles/boxes, at least 2 or 3 points must lie on the boundary.
- **Area Invariant:** The hull of $P$ must match the hull of $P \cup \{p_{int}\}$ where $p_{int}$ is an internal point.

### (2) Degenerate Cases
- **Fewer than 3 Points:** Point sets with 0, 1, or 2 points.
- **All Collinear:** The hull/box is a 1D line segment.

---

## 3. Proximity & Distances

**Algorithms:** Closest Pair, Convex Polygon Distance, Largest Empty Circle, Distance Map.

### (1) Testing Methods
- **Brute Force Comparison:** Check results against a $O(N^2)$ distance scan.
- **Zero Distance:** For intersecting convex polygons or duplicate points, distance must be exactly 0.
- **Voronoi Check:** Largest empty circle center must be a Voronoi vertex or lie on the boundary.

---

## 4. Intersections & Arrangements

**Algorithms:** Segment Intersection, Line Arrangement.

### (1) Testing Methods
- **Count Invariants:** For $N$ lines, maximum intersections $\leq N(N-1)/2$.
- **Euler Characteristic:** For line arrangements, $V - E + F = 1$.
- **Cross Checks:** Brute-force $O(N^2)$ segment intersection vs. sweep-line $O((N+I)\log N)$.

---

## 5. Polygon Operations & Properties

**Algorithms:** Polygon Properties (Area, Centroid), Point in Polygon, Polygon Boolean Operations, Minkowski Sum, Polygon Visibility, Medial Axis Polygon.

### (1) Testing Methods (Boolean Operations)
- **Idempotency:** `Union(A, A) = A`.
- **Commutativity:** `Union(A, B) = Union(B, A)`.
- **Empty Set:** `Union(A, Ø) = A`.
- **Area Conservation:** `Area(Union(A, B)) = Area(A) + Area(B) - Area(Intersection(A, B))`.

### (1) Testing Methods
- **Area Conservation:** `Area(A U B) = Area(A) + Area(B) - Area(A ∩ B)`.
- **Ray-Casting Invariance:** Point-in-polygon should yield the same result regardless of ray direction.
- **Medial Axis Reconstruction:** The union of circles centered on the medial axis should approximate the original polygon.

---

## 6. Polygon Partitioning & Decomposition

**Algorithms:** Convex Partition, Convex Decomposition, Identify Concave Parts, Art Gallery Problem.

### (1) Testing Methods
- **Reconstruction:** The union of all partitioned pieces must exactly equal the original polygon.
- **Convexity Check:** Every piece in a convex partition must be strictly convex.
- **Guard Coverage (Art Gallery):** The union of visibility polygons from all placed guards must cover the entire polygon.

---

## 7. Triangulation & Voronoi Diagrams

**Algorithms:** Triangulation (Ear-Clipping/Delaunay), Delaunay Flip, Dynamic Delaunay, Voronoi Diagram.

### (1) Testing Methods
- **Delaunay Property:** No point $P$ is inside the circumcircle of any triangle $T$.
- **Duality:** Verify Voronoi vertices are exactly the circumcenters of Delaunay triangles.
- **Area Conservation:** The sum of triangle areas must equal the polygon/hull area.

---

## 8. Planar Subdivisions & DCEL

**Algorithms:** Planar Subdivision (Point Location), Euler Characteristic.

### (1) Testing Methods
- **Euler Formula:** Check $V - E + F = 1 + C$ for planar graphs.
- **Traversal Consistency:** `edge.next.twin.next` must properly traverse the vertex umbrella.

---

## 9. Spatial Data Structures

**Algorithms:** Point KD-Tree 2D, Point Quadtree 2D, Point Simplification.

### (1) Testing Methods (R-tree)
- **Correctness:** Range queries and nearest neighbor searches must match brute-force results.
- **Structural Integrity:** Every node (except root) must have between $m$ and $M$ children.
- **Bounding Box Tightness:** A node's bounding box must be the minimum box containing all its children's boxes.

### (1) Testing Methods
- **Brute-Force Equivalence:** Range search and k-NN must exactly match a linear scan.
- **Idempotency:** Re-inserting the same data shouldn't break the tree.

---

## 10. Space-Filling Curves & Walks

**Algorithms:** Random Walker 2D/3D, Self-Avoiding Walk 2D, Spiral, Zigzag, Grid Walks, Hilbert, Morton, Peano.

### (1) Testing Methods
- **Bijectivity (Space-Filling):** The mapping from 1D index to 2D/3D coordinate must be 1-to-1 and onto for a given domain.
- **Self-Avoidance:** A SAW must never visit the same coordinate twice.

---

## 11. Mesh Algorithms

**Algorithms:** Triangle Mesh, Mesh Neighbors, Mesh Coloring, Mesh Transfer, Mesh Refinement, Mesh Reordering (Cuthill-McKee), Mesh Voxelization.

### (1) Testing Methods (Mesh Adjacency Matrix)
- **Symmetry:** The adjacency matrix must be symmetric for undirected meshes.
- **Trace/Diagonal:** The diagonal should be zero (no self-loops) unless specified.
- **Edge Count:** `Sum(Matrix) / 2` (for undirected) should equal the number of unique edges.

### (1) Testing Methods
- **Manifold Check:** Every edge shared by exactly 2 faces (for closed meshes).
- **Coloring Validity:** No two adjacent faces/vertices share the same color.
- **Bandwidth Reduction:** After Cuthill-McKee, the matrix bandwidth should be strictly $\leq$ the original bandwidth.

---

## 12. Circle Packing

### (1) Testing Methods
- **In-Polygon Test:** Every circle center `C` with radius `R` must satisfy `PointInPolygon(C)` and `Distance(C, PolygonBoundary) >= R`.
- **Non-Overlapping Test:** For any two circles with centers `C1, C2` and radius `R`, `Distance(C1, C2) >= 2*R`.
- **Density Verification:** Compare packed area `N * PI * R^2` against total polygon area.
- **Optimal Radius Search:** If searching for max radius for `N` circles, verify that `N+1` circles of the same radius do *not* fit (within a small tolerance).
- **Visual Validation:** Generate SVG/PNG and verify hexagonal pattern alignment.

### (2) Degenerate Cases
- **Radius > Polygon Width:** Zero circles should be packed.
- **Empty/Single-Point Polygons:** Handled gracefully without crashes.
- **Extremely Concave Polygons:** Circles should not "jump" across narrow gaps outside the polygon.

### (3) Common Failures
- **Boundary Leaks:** Circles centered near reflex vertices partially overlapping the exterior.
- **Precision Errors:** Floating point drift causing circles to be placed slightly outside the boundary.

---

## 13. Rectangle Packing

### (1) Testing Methods
- **Boundary Check:** For all packed rectangles `R_i`, `0 <= R_i.x` and `R_i.x + R_i.width <= ContainerWidth` (similarly for `y` and `height`).
- **Overlap Test:** For any `R_i, R_j`, the intersection area must be 0.
- **Efficiency Calculation:** `Sum(R_i.area) / (ContainerWidth * ContainerHeight)` must be <= 1.0.
- **Target Shape Consistency:** If `target_shape="square"`, verify `|ContainerWidth - ContainerHeight|` is minimized.
- **Ordering Invariants:** Test if sorting by area, height, or width produces different (valid) efficiencies.

### (2) Degenerate Cases
- **Zero-Dimension Rectangles:** Handled without division-by-zero errors.
- **Single Enormous Rectangle:** Should define the minimum container size.
- **Perfectly Uniform Rectangles:** Should pack into a grid with 100% efficiency if dimensions allow.

### (3) Common Failures
- **Heuristic Sub-optimality:** Packing failing to find a known-perfect fit due to poor choice of starting position.
- **Coordinate Drift:** Accumulating small errors in `x, y` placements leading to tiny overlaps.

---

## 14. Generation & Sampling

**Algorithms:** Generate Convex/Concave Shapes, Generate Triangle/Circle/Rectangle Points.

### (1) Testing Methods
- **Validation:** Generated convex shapes must pass the `is_convex` test.
- **Uniformity:** Point samplers should pass statistical tests (e.g., Monte Carlo integration checks) for uniform distribution.

---

## 15. Advanced Algorithms

**Algorithms:** Davenport-Schinzel Sequences, Polygonal Mean Curvature Flow.

### (1) Testing Methods
- **Sequence Validity:** Davenport-Schinzel sequences must not contain alternating subsequences of length $s+2$.
- **Smoothing Convergence:** Mean curvature flow should eventually shrink a non-self-intersecting polygon to a convex shape.

---

## 16. Spectral Geometry & PDE Solvers

**Algorithms:** HKS, WKS, Diffusion Distance, Walk on Spheres (WoS), Walk on Stars (WoSt).

### (1) Testing Methods
- **Distance Symmetry:** `DiffusionDistance(i, j) == DiffusionDistance(j, i)`.
- **Identity Property:** `DiffusionDistance(i, i)` should be effectively 0.
- **Monte Carlo Variance:** For WoS/WoSt, use large enough `num_walks` and verify results fall within expected statistical confidence intervals.
- **Linear Recovery:** WoSt gradient estimation should perfectly recover the gradient of a linear function (within statistical noise).
- **Eigenvalue Ordering:** Verify that eigenvalues are non-negative and non-decreasing.

### (2) Common Failures
- **Singular Laplacians:** Closed meshes or meshes with disconnected components causing numerical instability in eigenvalue solvers.
- **High Variance:** Stochastic solvers returning inconsistent results due to low sample counts.
- **Boundary Precision:** WoS "leaking" through boundaries if epsilon is too large relative to local feature size.
