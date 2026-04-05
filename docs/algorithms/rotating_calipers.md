# Rotating Calipers

## 1. Overview
Rotating calipers is a fundamental algorithmic paradigm in computational geometry used to solve several problems related to convex polygons in linear time. The technique is analogous to rotating a pair of parallel lines (the "calipers") around the boundary of a convex polygon, maintaining contact with the polygon at all times. It was first popularized by Godfried Toussaint in 1983 and has since become a standard tool for efficiency in geometric computing.

## 2. Definitions
*   **Antipodal Pair**: A pair of vertices $(u, v)$ such that there exist two parallel supporting lines through $u$ and $v$.
*   **Supporting Line**: A line through a vertex of a polygon such that the entire polygon lies on one side of the line.
*   **Diameter**: The maximum distance between any two points in a polygon (guaranteed to be an antipodal pair of vertices).
*   **Width**: The minimum distance between two parallel supporting lines.

## 3. Theory
The core idea of rotating calipers is that many properties of a convex polygon are determined by its **antipodal pairs**.
1.  Initialize the algorithm by finding two vertices that form an antipodal pair (e.g., the vertices with minimum and maximum $y$-coordinates).
2.  Imagine two parallel horizontal lines passing through these vertices.
3.  Rotate the lines until one of them coincides with an edge of the polygon.
4.  The new contact points form the next antipodal pair.
5.  Repeat this process until the lines have rotated by $180^\circ$.

During the rotation, the algorithm can calculate various metrics like distance, area, or width, depending on the specific problem being solved.

## 4. Pseudo code
```python
function RotatingCalipers(polygon):
    n = len(polygon)
    # 1. Find initial antipodal pair (min/max y)
    i = index_of_min_y(polygon)
    j = index_of_max_y(polygon)
    
    start_i, start_j = i, j
    
    # 2. Rotate until we come back to start
    while True:
        # 3. Calculate current metric (e.g., Diameter)
        current_dist = Distance(polygon[i], polygon[j])
        max_dist = max(max_dist, current_dist)
        
        # 4. Find the angles of the next edges
        angle_i = EdgeAngle(polygon, i)
        angle_j = EdgeAngle(polygon, j)
        
        # 5. Rotate the calipers by the smaller angle
        if angle_i < angle_j:
            i = (i + 1) % n
        else:
            j = (j + 1) % n
            
        if i == start_i and j == start_j:
            break
            
    return max_dist
```

## 5. Parameters Selections
*   **Problem Type**: The algorithm can be adapted for:
    *   **Diameter**: Max distance between vertices.
    *   **Width**: Min distance between supporting lines.
    *   **Minimum Bounding Box**: Min area/perimeter rectangle.
    *   **Convex Polygon Distance**: Min distance between two polygons.
    *   **Convex Polygon Intersection**: Detecting if two polygons overlap.

## 6. Complexity
*   **Time Complexity**: $O(n)$ where $n$ is the number of vertices in the convex hull. (The hull construction itself takes $O(n \log n)$).
*   **Space Complexity**: $O(1)$ auxiliary space beyond storing the vertices.

## 7. Usages
*   **Object Fitting**: Finding the smallest box or largest internal distance for a shape.
*   **Collision Detection**: Fast distance calculation between convex objects.
*   **Data Analysis**: Calculating the "spread" or "extent" of a set of data points.
*   **Computer Vision**: Estimating the orientation and aspect ratio of a segmented object.
*   **Robotics**: Path planning with clearance constraints.

## 8. Testing methods and Edge cases
*   **Regular Polygons**: For a square, the diameter should be the diagonal, and the width should be the side length.
*   **Points on a Line**: Diameter should be the distance between endpoints.
*   **Parallel Edges**: Ensure the algorithm handles cases where multiple edges are collinear with the calipers.
*   **Floating-Point Precision**: Use robust angle comparisons or cross-products to determine the rotation step.
*   **Small Polygons**: Verify correctness for $n=3$ (triangles).

## 9. References
*   Toussaint, G. T. (1983). "Solving geometric problems with the rotating calipers". Proceedings of MELECON '83.
*   Shamos, M. I. (1978). "Computational Geometry". PhD thesis, Yale University.
*   Preparata, F. P., & Shamos, M. I. (1985). "Computational Geometry: An Introduction". Springer-Verlag.
*   Wikipedia: [Rotating calipers](https://en.wikipedia.org/wiki/Rotating_calipers)
