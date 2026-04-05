# Minkowski Sums

## 1. Overview
The Minkowski sum of two sets of points $A$ and $B$ is the set of all possible sums of a point from $A$ and a point from $B$. In computational geometry, this operation is primarily used with polygons (2D) or polyhedra (3D). It is a fundamental tool for motion planning, collision detection, and calculating the offset of shapes.

## 2. Definitions
*   **Minkowski Sum ($A \oplus B$)**: $\{a + b \mid a \in A, b \in B\}$.
*   **Minkowski Difference ($A \ominus B$)**: $\{a - b \mid a \in A, b \in B\}$. This is used to check if two shapes intersect (intersect if $0 \in A \ominus B$).
*   **Convex Polygon**: A polygon where the Minkowski sum is easy to compute using edge reordering.

## 3. Theory
For two **convex polygons** $P$ and $Q$ with $n$ and $m$ vertices respectively, their Minkowski sum is also a convex polygon with at most $n+m$ vertices. The algorithm for computing it is as follows:
1.  Collect all the edges of $P$ and $Q$.
2.  Orient all edges counter-clockwise.
3.  Sort all edges by their polar angle.
4.  Chain the edges together starting from the sum of the bottom-left vertices of $P$ and $Q$.

For **non-convex polygons**, the Minkowski sum is much more complex. The standard approach is to:
1.  Decompose both non-convex polygons into convex pieces (e.g., using convex decomposition).
2.  Compute the Minkowski sum for every pair of convex pieces ($P_i \oplus Q_j$).
3.  Compute the union of all the resulting convex Minkowski sums.

## 4. Pseudo code
```python
function MinkowskiSumConvex(P, Q):
    # P and Q are CCW convex polygons
    edges_P = GetOrientedEdges(P)
    edges_Q = GetOrientedEdges(Q)
    
    # Sort all edges by polar angle
    all_edges = sorted(edges_P + edges_Q, key=lambda e: atan2(e.dy, e.dx))
    
    # Start at the sum of bottom-left vertices
    start_P = min(P, key=lambda p: (p.y, p.x))
    start_Q = min(Q, key=lambda p: (p.y, p.x))
    current = start_P + start_Q
    
    result = [current]
    for e in all_edges:
        current = current + e.vector
        result.append(current)
        
    return result[:-1] # Remove duplicate start/end
```

## 5. Parameters Selections
*   **Input Orientation**: Polygons MUST be oriented consistently (e.g., both CCW).
*   **Decomposition Method**: The choice of convex decomposition (exact vs. approximate) significantly affects the performance and complexity of the non-convex case.

## 6. Complexity
*   **Convex Case**: $O(n+m)$ time and space, where $n$ and $m$ are vertex counts.
*   **Non-Convex Case**: $O(n^2 m^2)$ in the worst case for simple polygons, due to the number of pairwise convex sums and the subsequent union operation.

## 7. Usages
*   **Motion Planning (Configuration Space)**: Expanding obstacles by the shape of the robot. If the robot's center is at $x$, it collides with obstacle $O$ if $x \in O \oplus (-Robot)$.
*   **Collision Detection**: The GJK (Gilbert-Johnson-Keerthi) algorithm uses Minkowski differences to check for intersections efficiently.
*   **CAD Offsetting**: Creating a "buffer" or "padding" around a shape (mitered offsets).
*   **Morphological Operations**: Dilation of 2D images or 3D volumes.

## 8. Testing methods and Edge cases
*   **Points and Lines**: Minkowski sum of a polygon and a single point is just a translation. Sum of a polygon and a line segment is a "swept" version of the polygon.
*   **Collinear Edges**: Edges from $P$ and $Q$ with the same angle should be merged into a single longer edge in the result.
*   **Degenerate Shapes**: Polygons with zero area or zero vertices.
*   **Non-Convex Union**: For non-convex sums, verify that internal "voids" are correctly handled or filled if necessary.
*   **Origin Symmetry**: Minkowski sum of $P$ and its reflection $-P$ is always centrally symmetric.

## 9. References
*   Guibas, L. J., & Seidel, R. (1987). "Computing convolutions by reciprocal search". Discrete & Computational Geometry.
*   Lozano-Pérez, T. (1983). "Spatial Planning: A Configuration Space Approach". IEEE Transactions on Computers.
*   Fogel, E., & Halperin, D. (2006). "Exact Minkowski Sums of Convex Polygons". CGAL Documentation.
*   [Wikipedia: Minkowski addition](https://en.wikipedia.org/wiki/Minkowski_addition)
