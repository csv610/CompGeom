# Convex Decomposition

## 1. Overview
Convex decomposition is the process of partitioning a non-convex (concave) polygon into a set of disjoint convex polygons. This is a fundamental operation in computational geometry, as many algorithms work more efficiently on convex shapes.

## 2. Definitions
*   **Convex Polygon:** A polygon where any line segment between two interior points lies entirely inside the polygon.
*   **Diagonal:** A line segment connecting two non-adjacent vertices of the polygon that lies entirely within the interior.

## 3. Theory
The implementation uses a **triangle merging** approach.
1. Triangulate the polygon (e.g., using ear clipping).
2. For each shared diagonal between two adjacent triangles/polygons, check if removing the diagonal results in a convex polygon.
3. If it does, merge the two parts.

## 4. Pseudo code
```python
Algorithm: Convex Decomposition (Triangle Merging)
Input: Concave polygon P
Output: Set of convex polygons {C_i}

1. T = Triangulate(P)
2. D = List of all interior diagonals of T
3. For each d in D:
4.   Let P1, P2 be the parts sharing diagonal d
5.   If Merged(P1, P2) is convex at endpoints of d:
6.     Merge P1 and P2 into a single part
7. Return final parts.
```

## 5. Parameters Selections
*   **Triangulation Algorithm:** Ear clipping is used for simplicity.

## 6. Complexity
*   **Time:** $O(n^2)$ for simple merging heuristics.
*   **Space:** $O(n)$.

## 7. Usages
Implemented in `compgeom.polygon.polygon_decomposer.convex_decompose_polygon`. Used in physics engines, motion planning, and collision detection.

## 8. Testing methods and Edge cases
*   **Testing:** Verify all resulting parts are convex. Check that the union of parts matches the original area.
*   **Edge Cases:** Polygons with holes, self-intersecting polygons (unsupported), highly narrow "snaky" polygons.

## 9. References
*   Hertel, S., & Mehlhorn, K. (1983). "Fast triangulation of simple polygons". FCT.
*   Wikipedia: [Polygon decomposition](https://en.wikipedia.org/wiki/Polygon_decomposition)
