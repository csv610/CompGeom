# Welzl's Algorithm (Smallest Enclosing Circle)

## 1. Overview
Welzl's algorithm is a randomized algorithm for finding the smallest enclosing circle (the minimum-area circle that contains all points in a set). Originally described by Emo Welzl in 1991, it is a brilliant application of the linear programming paradigm to a geometric problem. It achieves an expected $O(n)$ time complexity, making it highly efficient for point sets in 2D.

## 2. Definitions
*   **Smallest Enclosing Circle (SEC)**: The unique circle with the minimum possible radius that contains all points of a given set $P$.
*   **Support Points**: The points of $P$ that lie on the boundary of the SEC. At most 3 points are needed to uniquely define the circle.
*   **Random Permutation**: The points are processed in a random order to ensure the $O(n)$ expected time complexity.

## 3. Theory
The algorithm is based on a recursive reduction of the point set. The key insight is that if a new point $P_i$ is already inside the SEC of the previous $i-1$ points, then the SEC remains the same. If $P_i$ is outside, it MUST lie on the boundary of the new SEC. This allows us to recursively solve the problem with $P_i$ fixed as a "boundary point."

The recursion continues until we have a set of 0, 1, 2, or 3 points that must lie on the boundary. These "fixed" points uniquely define the circle (0: none, 1: point as center, 2: segment as diameter, 3: circumcircle).

## 4. Pseudo code
```python
function Welzl(P, R=[]):
    if len(P) == 0 or len(R) == 3:
        return CircleFromBoundary(R)
        
    # 1. Choose a point and remove it
    p = P.pop()
    
    # 2. Find the smallest enclosing circle of the remaining points
    D = Welzl(P.copy(), R)
    
    # 3. If the removed point is inside the circle, it's the SEC
    if p is in D:
        return D
        
    # 4. Otherwise, p must be on the boundary of the SEC
    return Welzl(P.copy(), R + [p])

# To start:
random.shuffle(points)
SEC = Welzl(points)
```

## 5. Parameters Selections
*   **Randomization**: Shuffling the input points at the beginning is crucial. Without randomization, structured input (like points on a line) can cause $O(n^2)$ worst-case performance.
*   **Numerical Precision**: Circumcircle calculations for 3 points can be sensitive to collinearity. An epsilon should be used to check if 3 points are nearly on a line.

## 6. Complexity
*   **Time Complexity**: $O(n)$ expected. Although the recursion depth is $n$, the probability that a point falls outside the current circle decreases rapidly, leading to the $O(n)$ bound.
*   **Space Complexity**: $O(n)$ for the recursion stack and the copies of the point set.

## 7. Usages
*   **Collision Detection**: Generating a bounding sphere for an object as a fast first-pass check.
*   **Facility Location**: Finding the center for a new resource (e.g., a cell tower) to cover all clients with minimum range.
*   **Cluster Analysis**: Determining the spatial extent of a group of points.
*   **Camera Control**: Finding the minimum zoom/pan to keep all characters in a scene visible.

## 8. Testing methods and Edge cases
*   **Collinear Points**: The SEC should have its diameter equal to the distance between the two furthest points.
*   **Duplicate Points**: Handled naturally by the inclusion check.
*   **Small Sets**: Verify with 0, 1, and 2 points.
*   **Symmetry**: Regular polygons should result in a circle centered at the polygon's centroid.
*   **Redundant Points**: Verify that a million points inside a circle don't change the SEC defined by 3 points on the boundary.

## 9. References
*   Welzl, E. (1991). "Smallest enclosing disks (balls and ellipsoids)". Lecture Notes in Computer Science.
*   Megiddo, N. (1983). "Linear-time algorithms for linear programming in R^3 and related problems". SIAM Journal on Computing.
*   Wikipedia: [Smallest-circle problem](https://en.wikipedia.org/wiki/Smallest-circle_problem)
