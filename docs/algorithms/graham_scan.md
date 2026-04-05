# Graham Scan (Convex Hull)

## 1. Overview
The Graham scan is an efficient method for computing the convex hull of a finite set of points in the Euclidean plane. It was published by Ronald Graham in 1972 and is a fundamental algorithm in computational geometry. The algorithm finds all vertices of the convex hull ordered along its boundary.

## 2. Definitions
*   **Convex Hull**: The smallest convex set that contains all the points in a given set.
*   **Cross Product (2D)**: For three points $A, B, C$, the cross product $(B.x - A.x)(C.y - A.y) - (B.y - A.y)(C.x - A.x)$ determines the orientation:
    *   Positive: Left turn (Counter-clockwise)
    *   Negative: Right turn (Clockwise)
    *   Zero: Collinear
*   **Anchor Point**: The point with the lowest y-coordinate (and lowest x-coordinate in case of ties), guaranteed to be on the convex hull.

## 3. Theory
The algorithm operates by first identifying an extreme point (the anchor) and sorting all other points based on the polar angle they make with this anchor. It then performs a linear scan through the sorted points, maintaining a stack of points that potentially form the hull. For each new point, the algorithm "backtracks" by popping points from the stack that would create a non-convex (right) turn. This ensures that the final stack contains only the vertices of the convex hull in counter-clockwise order.

## 4. Pseudo code
```python
function GrahamScan(points):
    if len(points) <= 2: return points
    
    # 1. Find anchor point
    anchor = min(points, key=lambda p: (p.y, p.x))
    
    # 2. Sort points by polar angle with anchor
    # Use cross product for sorting to avoid trigonometric functions
    sorted_points = sorted(points, key=polar_angle_with_anchor)
    
    # 3. Process points
    hull = []
    for p in sorted_points:
        while len(hull) >= 2 and cross_product(hull[-2], hull[-1], p) <= 0:
            hull.pop()
        hull.append(p)
        
    return hull
```

## 5. Parameters Selections
*   **Input**: A list of `Point2D` objects.
*   **Sorting Criterion**: Polar angle relative to the anchor. In the implementation, `math.atan2` is often used, but cross-products can provide a more robust (and sometimes faster) comparison.

## 6. Complexity
*   **Time Complexity**: $O(n \log n)$, where $n$ is the number of points. This is dominated by the sorting step. The subsequent scan takes $O(n)$ time because each point is pushed and popped at most once.
*   **Space Complexity**: $O(n)$ to store the sorted points and the stack.

## 7. Usages
*   Collision detection in physics engines.
*   Shape analysis and pattern recognition.
*   Geographic Information Systems (GIS) for defining boundary regions.
*   Minimum bounding box calculations.

## 8. Testing methods and Edge cases
*   **Few Points**: 0, 1, or 2 points should return the input points.
*   **Collinear Points**: Points lying on the same line. The algorithm should handle them by either including them or only keeping the endpoints (depending on the `cross_product <= 0` vs `< 0` logic).
*   **Duplicate Points**: Multiple points at the same coordinates.
*   **Degenerate Cases**: All points at the same location.
*   **Vertical/Horizontal alignment**: Points forming a perfect grid.

## 9. References
*   Graham, R. L. (1972). "An Efficient Algorithm for Determining the Convex Hull of a Finite Planar Set". Information Processing Letters.
*   Cormen, T. H., Leiserson, C. E., Rivest, R. L., & Stein, C. (2009). "Introduction to Algorithms". MIT Press.
*   [Wikipedia: Graham scan](https://en.wikipedia.org/wiki/Graham_scan)
