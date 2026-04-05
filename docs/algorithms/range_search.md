# Range Search

## 1. Overview
Range searching is a fundamental task in computational geometry where the goal is to efficiently retrieve all geometric objects (typically points) that lie within a specified query region (the "range"). Query regions are usually simple shapes like axis-aligned rectangles (orthogonal range search), circles, or half-planes. Efficient range searching is the backbone of spatial databases, geographic information systems (GIS), and computer graphics.

## 2. Definitions
*   **Point Set (P)**: A set of $n$ points in $d$-dimensional space.
*   **Query Range (R)**: A region in space (e.g., a hyper-rectangle $[x_1, x_2] \times [y_1, y_2]$).
*   **Range Reporting**: Returning the actual list of points $\{p \in P \mid p \in R\}$.
*   **Range Counting**: Returning only the number of points $k = |\{p \in P \mid p \in R\}|$.
*   **Preprocessing**: The one-time cost of building a data structure to speed up future queries.

## 3. Theory
The efficiency of range search depends on the dimensionality and the type of range.
1.  **1D Range Search**: Solved using a balanced binary search tree in $O(\log n + k)$ time.
2.  **Orthogonal Range Search (d-dimensions)**:
    *   **KD-Trees**: Good for medium dimensions; $O(\sqrt{n} + k)$ query time in 2D.
    *   **Range Trees**: Faster query time $O(\log^d n + k)$ but higher space $O(n \log^{d-1} n)$.
    *   **Quadtrees**: Effective for non-uniform data distributions.
3.  **Circular/Spherical Range Search**: Often handled using KD-trees with a distance-based pruning condition or specialized structures like **Ball Trees**.
4.  **Non-Orthogonal Range Search**: General shapes can be approximated by rectangles or handled using more complex structures like **Simplex Range Reporting**.

The fundamental tradeoff in range search is between **Query Time**, **Preprocessing Time**, and **Space Complexity**.

## 4. Pseudo code
### General Hierarchical Range Search
```python
function RangeSearch(node, query_range, results):
    # 1. Base case: node is empty
    if node is None: return
    
    # 2. Pruning: query range does not intersect node's bounding box
    if not Intersect(node.bbox, query_range):
        return
        
    # 3. Acceptance: node's bounding box is fully inside query range
    if FullyContains(query_range, node.bbox):
        # Add all points in this subtree without further recursion
        results.extend(node.all_points)
        return
        
    # 4. Partial Overlap: Check points in current node and recurse
    if node.is_leaf:
        for p in node.points:
            if query_range.contains(p):
                results.append(p)
    else:
        for child in node.children:
            RangeSearch(child, query_range, results)
```

## 5. Parameters Selections
*   **Dimensionality**: For $d > 20$, most spatial data structures degrade to linear search (the "Curse of Dimensionality").
*   **Data Distribution**: Use **Quadtrees** or **R-Trees** for highly clustered data; use **KD-Trees** or **Range Trees** for more uniform data.
*   **Memory**: If memory is tight, KD-trees are preferred ($O(n)$ space).

## 6. Complexity Summary
| Structure | Space | Query (2D Reporting) |
| :--- | :--- | :--- |
| KD-Tree | $O(n)$ | $O(\sqrt{n} + k)$ |
| Range Tree | $O(n \log n)$ | $O(\log^2 n + k)$ |
| Quadtree | $O(depth \cdot n)$ | $O(depth + k)$ |
| R-Tree | $O(n)$ | $O(\log n + k)$ (avg) |

## 7. Usages
*   **Spatial Databases**: Finding all customers within a specific zip code or radius.
*   **Computer Graphics**: Frustum culling and identifying all objects hit by a blast radius.
*   **GIS**: Overlaying different map layers (e.g., finding all houses in a flood zone).
*   **Machine Learning**: Preprocessing for K-Nearest Neighbors (KNN).
*   **Collision Detection**: Finding all pairs of objects that might be colliding.

## 8. Testing methods and Edge cases
*   **Empty Query**: Ensure the algorithm returns an empty list for a range containing no points.
*   **Full Range Query**: Verify that a range covering the entire domain returns all $n$ points.
*   **Points on Boundaries**: Consistently handle points exactly on the edge of the query rectangle.
*   **Overlapping Points**: Ensure duplicate points are correctly counted/reported.
*   **Very Large Coordinates**: Precision check for queries far from the origin.

## 9. References
*   Bentley, J. L. (1975). "Multidimensional binary search trees used for associative searching". Communications of the ACM.
*   Lueker, G. S. (1978). "A data structure for orthogonal range queries". IEEE FOCS.
*   Berg, M. de, Cheong, O., Kreveld, M. van, & Overmars, M. (2008). "Computational Geometry: Algorithms and Applications". Springer-Verlag.
*   Wikipedia: [Range searching](https://en.wikipedia.org/wiki/Range_searching)
