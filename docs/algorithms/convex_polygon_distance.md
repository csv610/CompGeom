# Convex Polygon Distance

## 1. Overview
The convex polygon distance problem involves finding the minimum Euclidean distance between two non-intersecting convex polygons $P$ and $Q$. This is a fundamental operation in collision detection and motion planning. While a naive $O(n \cdot m)$ approach checks all pairs of edges, more efficient algorithms leverage the convexity of the shapes to achieve $O(n + m)$ or even $O(\log n + \log m)$ performance.

## 2. Definitions
*   **Euclidean Distance ($dist(P, Q)$)**: $\min \| p - q \|$ where $p \in P$ and $q \in Q$.
*   **Separating Axis**: A line such that the projections of two convex shapes onto the line do not overlap.
*   **Support Point**: For a given direction $d$, the point in a polygon that is furthest in that direction.
*   **GJK Algorithm**: Gilbert-Johnson-Keerthi algorithm, a widely used method for distance calculation using the Minkowski difference.

## 3. Theory
The most common approach for linear-time distance calculation is based on the **Rotating Calipers** method.
1.  Find the pair of points (one on each polygon) that minimize the distance. For non-intersecting convex polygons, this minimum distance occurs between two vertices, or a vertex and an edge.
2.  Use the rotating calipers technique to "crawl" around both polygons simultaneously. Because the polygons are convex, the distance function is unimodal along the boundary, allowing us to find the global minimum in a single pass.

Another powerful approach is the **GJK Algorithm**:
1.  Compute the **Minkowski Difference** $D = P \ominus Q$.
2.  The distance between $P$ and $Q$ is the distance from the origin $(0,0)$ to the set $D$.
3.  GJK iteratively builds a simplex inside $D$ that gets closer and closer to the origin.

## 4. Pseudo code
### Rotating Calipers for Distance
```python
function ConvexDistance(P, Q):
    # 1. Initialize indices to points with min/max y
    i = index_of_min_y(P)
    j = index_of_max_y(Q)
    
    min_dist = infinity
    
    # 2. Rotate calipers around both polygons
    for _ in range(len(P) + len(Q)):
        # Calculate current distance (vertex-vertex or vertex-edge)
        d = Distance(P[i], Q[j])
        min_dist = min(min_dist, d)
        
        # 3. Determine which caliper to rotate next
        angle_P = AngleOfEdge(P, i)
        angle_Q = AngleOfEdge(Q, j)
        
        if angle_P < angle_Q:
            i = (i + 1) % len(P)
        else:
            j = (j + 1) % len(Q)
            
    return min_dist
```

## 5. Parameters Selections
*   **Polygon Orientation**: Polygons must be consistently oriented (e.g., both CCW).
*   **Initial Points**: Starting at extreme points ensures the calipers are correctly synchronized.

## 6. Complexity
*   **Time Complexity**: $O(n + m)$ using rotating calipers or GJK. Binary search methods can achieve $O(\log n + \log m)$ for preprocessed polygons.
*   **Space Complexity**: $O(1)$ auxiliary space if the polygons are already stored.

## 7. Usages
*   **Collision Avoidance**: Maintaining a "safety buffer" between a robot and obstacles.
*   **Physics Simulation**: Calculating the time of impact or the depth of penetration.
*   **Tolerance Analysis**: Determining if two mechanical parts will fit together with a required clearance.
*   **UI Layout**: Calculating the spacing between complex geometric buttons or containers.

## 8. Testing methods and Edge cases
*   **Intersecting Polygons**: The distance should be 0. (GJK handles this by detecting that the origin is inside the Minkowski difference).
*   **Parallel Edges**: The minimum distance might be achieved along an entire segment.
*   **Points and Lines**: Test with "polygons" that are actually single points or line segments.
*   **Very Thin Polygons**: Ensure numerical stability for nearly collinear vertices.
*   **Vast Scales**: Precision check for polygons that are very far apart.

## 9. References
*   Toussaint, G. T. (1983). "Solving geometric problems with the rotating calipers". Proceedings of MELECON '83.
*   Gilbert, E. G., Johnson, D. W., & Keerthi, S. S. (1988). "A fast procedure for computing the distance between complex objects in three-dimensional space". IEEE Journal on Robotics and Automation.
*   Edelsbrunner, H. (1985). "Computing the extreme distances between two convex polygons". Journal of Algorithms.
*   Wikipedia: [Gilbert–Johnson–Keerthi distance algorithm](https://en.wikipedia.org/wiki/Gilbert%E2%80%93Johnson%E2%80%93Keerthi_distance_algorithm)
