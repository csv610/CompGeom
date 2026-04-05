# Polygon Boolean Operations

## 1. Overview
Polygon Boolean operations are a set of geometric algorithms used to compute the result of applying set operations (union, intersection, difference, and symmetric difference) to two or more polygons. These operations are essential in computer graphics, CAD/CAM, and GIS for manipulating complex shapes and defining regions of interest.

## 2. Definitions
*   **Union ($\cup$)**: The region covered by at least one of the input polygons.
*   **Intersection ($\cap$)**: The region shared by all input polygons.
*   **Difference ($A - B$)**: The region inside polygon A but outside polygon B.
*   **Symmetric Difference ($A \Delta B$)**: The region inside either A or B, but not both.
*   **Winding Rule**: A rule (e.g., Even-Odd or Non-Zero) used to determine the "inside" of a self-intersecting or hole-containing polygon.

## 3. Theory
The most common approach to polygon Boolean operations is based on **edge clipping and subdivision**. The algorithm typically involves:
1.  **Intersection Detection**: Finding all points where edges of polygon A intersect edges of polygon B.
2.  **Edge Subdivision**: Splitting edges at intersection points into smaller segments.
3.  **Edge Classification**: For each segment, determining if it is "Inside," "Outside," or "Shared" relative to the other polygon.
4.  **Loop Assembly**: Collecting the appropriate segments based on the desired operation (e.g., for Union, keep all "Outside" segments and "Shared" segments of the same orientation) and assembling them into new closed loops.

## 4. Pseudo code
```python
function PolygonBoolean(A, B, operation):
    # 1. Split edges at intersection points
    subdivided_A = SplitEdges(A, B)
    subdivided_B = SplitEdges(B, A)
    
    # 2. Classify segments
    classified_A = Classify(subdivided_A, B)
    classified_B = Classify(subdivided_B, A)
    
    # 3. Filter segments based on operation
    result_segments = []
    if operation == "UNION":
        result_segments += [s for s in classified_A if s.is_outside]
        result_segments += [s for s in classified_B if s.is_outside]
    elif operation == "INTERSECTION":
        result_segments += [s for s in classified_A if s.is_inside]
        result_segments += [s for s in classified_B if s.is_inside]
        
    # 4. Assemble into polygons
    return AssemblePolygons(result_segments)
```

## 5. Parameters Selections
*   **Precision (Epsilon)**: Crucial for determining if a vertex lies on an edge or if two edges are collinear.
*   **Winding Rule**: Must be consistent between input polygons (e.g., both CCW).

## 6. Complexity
*   **Time Complexity**: $O((n+m+k) \log (n+m))$ where $n, m$ are vertex counts and $k$ is the number of intersections, using a sweep-line algorithm (Bentley-Ottmann).
*   **Space Complexity**: $O(n+m+k)$ to store the subdivided edges and the resulting polygon.

## 7. Usages
*   **CSG (Constructive Solid Geometry)**: Building complex 3D objects from simple primitives.
*   **GIS Clipping**: Extracting spatial data within a specific boundary (e.g., finding all roads in a county).
*   **PCB Design**: Calculating overlapping areas of copper layers or solder masks.
*   **UI Layout**: Determining visible regions of windows and buttons.

## 8. Testing methods and Edge cases
*   **Collinear Edges**: Edges that overlap exactly or partially.
*   **Shared Vertices**: Polygons touching at a single point or along a common edge.
*   **Holes**: Polygons containing internal voids or "islands."
*   **Self-Intersecting Inputs**: May require preprocessing into a set of simple polygons.
*   **Degeneracies**: Zero-area polygons resulting from subtraction.

## 9. References
*   Vatti, B. R. (1992). "A generic solution to polygon clipping". Communications of the ACM.
*   Greiner, G., & Hormann, K. (1998). "Efficient clipping of arbitrary polygons". ACM TOG.
*   Weiler, K., & Atherton, P. (1977). "Hidden surface removal using polygon area subdivision". SIGGRAPH.
*   [Wikipedia: Boolean operations on polygons](https://en.wikipedia.org/wiki/Boolean_operations_on_polygons)
