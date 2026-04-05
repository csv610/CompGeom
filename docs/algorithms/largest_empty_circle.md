# Largest Empty Circle

## 1. Overview
The largest empty circle problem asks for the circle of maximum radius whose center is within the convex hull of a given set of points $P$, and whose interior contains no points from $P$. This problem is a fundamental challenge in computational geometry with direct applications in facility location and urban planning.

## 2. Definitions
*   **Empty Circle**: A circle whose interior contains no points from the set $P$.
*   **Voronoi Vertex**: A point where three or more Voronoi cells meet; it is equidistant to its closest three sites.
*   **Convex Hull (CH)**: The boundary of the set $P$. The center of the largest empty circle must be within the CH to prevent it from being at infinity.

## 3. Theory
The largest empty circle must have its center at one of two types of locations:
1.  **Voronoi Vertices**: A Voronoi vertex is the circumcenter of three points from $P$. If this vertex is inside the convex hull, it defines an empty circle passing through those three points.
2.  **Intersection of Voronoi Edges and Convex Hull**: The center could be at the intersection of a Voronoi edge and an edge of the convex hull.

The algorithm for finding the largest empty circle is:
1.  Compute the **Voronoi Diagram** of the points $P$.
2.  Iterate through all Voronoi vertices. For each vertex inside the convex hull, calculate the distance to its closest point (its radius).
3.  Iterate through all intersections of Voronoi edges with the convex hull boundary. For each intersection, calculate the radius of the empty circle centered there.
4.  The largest of all these radii defines the largest empty circle.

## 4. Pseudo code
```python
function LargestEmptyCircle(points):
    # 1. Compute Convex Hull and Voronoi Diagram
    CH = ConvexHull(points)
    VD = Voronoi(points)
    
    max_radius = 0
    best_center = None
    
    # 2. Check Voronoi Vertices
    for v in VD.vertices:
        if PointInPolygon(v, CH):
            r = Distance(v, VD.GetClosestSite(v))
            if r > max_radius:
                max_radius = r
                best_center = v
                
    # 3. Check Voronoi Edge intersections with CH
    for edge in VD.edges:
        for ch_edge in CH.edges:
            p = Intersect(edge, ch_edge)
            if p is not None:
                r = Distance(p, VD.GetClosestSite(p))
                if r > max_radius:
                    max_radius = r
                    best_center = p
                    
    return best_center, max_radius
```

## 5. Parameters Selections
*   **Precision**: Finding the intersection of Voronoi edges and the convex hull requires careful handling of floating-point inaccuracies.
*   **Region Constraint**: The problem can be generalized to find the largest empty circle within any bounding polygon (not just the convex hull).

## 6. Complexity
*   **Time Complexity**: $O(n \log n)$ to build the Voronoi diagram and convex hull. Finding intersections takes $O(n \log n)$ or $O(n)$ depending on the implementation.
*   **Space Complexity**: $O(n)$ to store the Voronoi and convex hull structures.

## 7. Usages
*   **Facility Location**: Finding the location for a new facility (e.g., a toxic waste dump or a new shopping center) that is as far as possible from all existing points of interest.
*   **Urban Planning**: Determining where to place a new park to maximize the distance from the nearest noise sources.
*   **Robotics**: Path planning to stay as far from obstacles as possible (the "safest" path follows Voronoi edges).
*   **Signal Coverage**: Identifying the largest "blind spot" in a cellular or Wi-Fi network.

## 8. Testing methods and Edge cases
*   **Square/Rectangle Alignment**: For four points in a square, the center should be at the centroid.
*   **Points on a Circle**: All Voronoi vertices should coincide at the center of the circle.
*   **Collinear Points**: The convex hull is a line segment, so the circle will have zero radius.
*   **Sparse vs. Dense**: Ensure the algorithm handles large empty spaces correctly.
*   **Large Coordinates**: Precision check for very large $x, y$.

## 9. References
*   Shamos, M. I., & Hoey, D. (1975). "Closest-point problems". IEEE FOCS.
*   Preparata, F. P., & Shamos, M. I. (1985). "Computational Geometry: An Introduction". Springer-Verlag.
*   Wikipedia: [Largest empty sphere](https://en.wikipedia.org/wiki/Largest_empty_sphere)
