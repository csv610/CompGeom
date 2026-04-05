# Monotone Decomposition

## 1. Overview
Monotone decomposition is the process of partitioning a simple polygon into a set of monotone polygons. A polygon is monotone with respect to a line $L$ if every line orthogonal to $L$ intersects the polygon in at most one connected component (a single line segment). This is typically a preprocessing step for more efficient polygon triangulation, as monotone polygons can be triangulated in linear time.

## 2. Definitions
*   **Monotone Polygon**: A polygon that is monotone with respect to a given line (usually the y-axis).
*   **Y-Monotone**: A polygon where any horizontal line intersects the interior at most once.
*   **Cusp Vertices**: Vertices where both neighbors have higher (start/split) or lower (end/merge) y-coordinates.
    *   **Start Vertex**: Interior is below; neighbors have higher y.
    *   **Split Vertex**: Interior is below; neighbors have higher y.
    *   **End Vertex**: Interior is above; neighbors have lower y.
    *   **Merge Vertex**: Interior is above; neighbors have lower y.

## 3. Theory
The algorithm uses a **plane sweep** approach, moving a horizontal line from top to bottom. The key to making a polygon y-monotone is to eliminate all split and merge vertices by adding diagonals. A split vertex is connected to a vertex above it (the "helper" of the edge to its left), and a merge vertex is connected to a vertex below it when the sweep line reaches it. By the time the sweep is finished, all cusps that violated monotonicity are resolved.

## 4. Pseudo code
```python
function MonotoneDecomposition(polygon):
    # 1. Sort vertices by y-coordinate (descending)
    events = sorted(polygon.vertices, key=lambda v: (-v.y, v.x))
    
    # 2. Sweep line status (active edges to the left/right of the sweep line)
    status = BalancedBST() 
    diagonals = []
    
    for v in events:
        if IsStartVertex(v):
            HandleStartVertex(v, status)
        elif IsEndVertex(v):
            HandleEndVertex(v, status, diagonals)
        elif IsSplitVertex(v):
            HandleSplitVertex(v, status, diagonals)
        elif IsMergeVertex(v):
            HandleMergeVertex(v, status, diagonals)
        else:
            HandleRegularVertex(v, status, diagonals)
            
    return SplitPolygon(polygon, diagonals)
```

## 5. Parameters Selections
*   **Sweep Direction**: Usually vertical (y-axis), but can be any arbitrary direction if the polygon is rotated.
*   **Data Structures**: A balanced binary search tree (BST) for the status and a priority queue for events are standard.

## 6. Complexity
*   **Time Complexity**: $O(n \log n)$ due to the sorting of vertices and the $O(\log n)$ operations on the balanced BST for each vertex.
*   **Space Complexity**: $O(n)$ to store the polygon, the status tree, and the resulting diagonals.

## 7. Usages
*   **Triangulation**: The first stage of $O(n \log n)$ polygon triangulation algorithms.
*   **Trapezoidal Decomposition**: Often used in conjunction with monotone partitioning.
*   **Path Planning**: Simplifying complex obstacles into monotone regions for easier navigation.

## 8. Testing methods and Edge cases
*   **Horizontal Edges**: Vertices with identical y-coordinates require consistent tie-breaking in the sort.
*   **Complex Cusps**: Multiple split/merge vertices at the same height.
*   **Strict Monotonicity**: Ensuring that horizontal lines intersecting a vertex or edge are handled correctly.
*   **Non-Simple Polygons**: Monotone decomposition is generally defined for simple polygons; holes require special handling (treating them as merge/split events).

## 9. References
*   Berg, M. de, Cheong, O., Kreveld, M. van, & Overmars, M. (2008). "Computational Geometry: Algorithms and Applications". Springer-Verlag.
*   Lee, D. T., & Preparata, F. P. (1977). "Location of a point in a planar subdivision and its applications". SIAM Journal on Computing.
*   [Wikipedia: Monotone polygon](https://en.wikipedia.org/wiki/Monotone_polygon)
