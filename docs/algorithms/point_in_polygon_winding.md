# Point in Polygon (Winding Number)

## 1. Overview
The Winding Number algorithm is a robust method for determining whether a point lies inside a given polygon. It calculates the total number of times the polygon's boundary wraps around the test point. A winding number of zero indicates the point is outside the polygon, while a non-zero value indicates it is inside. This method is particularly superior to the Ray Casting algorithm when dealing with self-intersecting polygons.

## 2. Definitions
*   **Winding Number ($wn$ )**: The integer number of times a closed curve (the polygon) rotates counter-clockwise around a point.
*   **Upward Crossing**: A polygon edge that starts below the point's y-coordinate and ends above it.
*   **Downward Crossing**: A polygon edge that starts above the point's y-coordinate and ends below it.
*   **Is-Left Test**: A geometric predicate that determines if a point is to the left, right, or on an oriented line segment.

## 3. Theory
The algorithm counts the net number of full revolutions the polygon makes around the point $P$. As we traverse the polygon's edges:
*   Every time an edge crosses the positive x-ray of $P$ going **upward**, we increment the winding number.
*   Every time an edge crosses the positive x-ray of $P$ going **downward**, we decrement the winding number.

Crucially, an edge is only counted if the point $P$ is actually to the left of the upward edge (or to the right of the downward edge), ensuring that the crossing actually "wraps" around the point.

## 4. Pseudo code
```python
function PointWindingNumber(P, polygon):
    wn = 0
    for each edge (V1, V2) in polygon:
        if V1.y <= P.y:
            if V2.y > P.y: # Potential upward crossing
                if IsLeft(V1, V2, P) > 0: # P is to the left of the edge
                    wn += 1
        else:
            if V2.y <= P.y: # Potential downward crossing
                if IsLeft(V1, V2, P) < 0: # P is to the right of the edge
                    wn -= 1
    return wn

function IsLeft(V1, V2, P):
    # Cross product (V2 - V1) x (P - V1)
    return (V2.x - V1.x) * (P.y - V1.y) - (P.x - V1.x) * (V2.y - V1.y)
```

## 5. Parameters Selections
*   **Input**: A test `Point2D` and a list of `Point2D` vertices representing the polygon.
*   **Winding Rule**: Most applications use the **Non-Zero Winding Rule** (inside if $wn \ne 0$), though some use the **Odd-Even Rule** ($wn$ is odd).

## 6. Complexity
*   **Time Complexity**: $O(n)$ where $n$ is the number of vertices. Each edge is visited exactly once.
*   **Space Complexity**: $O(1)$ auxiliary space, assuming the polygon vertices are already stored.

## 7. Usages
*   **SVG/PostScript Rendering**: Determining which areas of a complex path should be filled.
*   **GIS Analysis**: Checking if a GPS coordinate falls within a specific territorial boundary.
*   **Video Games**: Hitbox detection for complex, non-convex characters or objects.

## 8. Testing methods and Edge cases
*   **Point on Edge/Vertex**: The algorithm's behavior on the boundary depends on the strictness of the inequalities ($<$ vs $\le$).
*   **Horizontal Edges**: Handled correctly because they fail both the `V1.y <= P.y < V2.y` and `V2.y <= P.y < V1.y` conditions.
*   **Self-intersecting Polygons**: A "figure-eight" polygon will have regions with winding numbers of 1, -1, and 0.
*   **Degenerate Polygons**: Polygons with fewer than 3 vertices or zero area.

## 9. References
*   Sunday, D. (2001). "Inclusion of a Point in a Polygon". Journal of Graphics Tools.
*   Hormann, K., & Agathos, A. (2001). "The point in polygon problem for arbitrary polygons". Computational Geometry.
*   [Wikipedia: Point in polygon](https://en.wikipedia.org/wiki/Point_in_polygon)
