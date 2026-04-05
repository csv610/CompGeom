# QuickHull (Convex Hull)

## 1. Overview
QuickHull is a divide and conquer algorithm for computing the convex hull of a finite set of points. It is similar in design to the Quicksort sorting algorithm. It was independently published by several researchers, including Barber et al. (1996), and is the basis of the widely used `Qhull` library.

## 2. Definitions
*   **Convex Hull**: The smallest convex set containing all points.
*   **Distance from Line**: The perpendicular distance from a point to a line segment. Points farthest from a line segment are guaranteed to be vertices of the convex hull.
*   **Orientation**: Determining which side of a line a point lies on using the 2D cross-product.

## 3. Theory
The algorithm begins by finding the leftmost and rightmost points, which are guaranteed to be on the hull. These points divide the point set into two subsets by a line. For each subset, the point farthest from the line is identified. This point, along with the two original points, forms a triangle. Points inside this triangle cannot be on the convex hull and are discarded. The process is then recursively applied to the two edges of the triangle that are not part of the original line.

## 4. Pseudo code
```python
function QuickHull(points):
    leftmost = min(points)
    rightmost = max(points)
    
    # 1. Divide points into two sets based on the line (leftmost, rightmost)
    upper = points above line
    lower = points below line
    
    # 2. Recursively find hull vertices for each subset
    hull = [leftmost] + FindHull(leftmost, rightmost, upper) + 
           [rightmost] + FindHull(rightmost, leftmost, lower)
    return hull

function FindHull(A, B, candidates):
    if not candidates: return []
    
    # 1. Find point P farthest from line AB
    P = max(candidates, key=dist_from_line_AB)
    
    # 2. Divide remaining points into those left of AP and left of PB
    left_of_AP = [p for p in candidates if is_left_of(A, P, p)]
    left_of_PB = [p for p in candidates if is_left_of(P, B, p)]
    
    # 3. Recursively build the hull
    return FindHull(A, P, left_of_AP) + [P] + FindHull(P, B, left_of_PB)
```

## 5. Parameters Selections
*   **Input**: A set of points (list of `Point2D`).
*   **Recursive termination**: When the subset of candidate points for a segment is empty.

## 6. Complexity
*   **Time Complexity**: Average case $O(n \log n)$. Worst case $O(n^2)$ when points are distributed such that the partition is highly unbalanced (e.g., points on a circle).
*   **Space Complexity**: $O(n)$ to store the points and recursion stack.

## 7. Usages
*   The primary algorithm in the `Qhull` library, used by SciPy, MATLAB, and R.
*   General-purpose convex hull calculation in 2D and 3D.
*   Collision detection and mesh simplification.

## 8. Testing methods and Edge cases
*   **Highly Symmetric Points**: Points on a circle can lead to the worst-case $O(n^2)$ performance.
*   **Collinear Points**: Farthest point might not be unique; handle tie-breaking consistently.
*   **Points inside the hull**: Ensure that the pruning (ignoring points inside triangles) is correct.
*   **Numerical Precision**: Use an epsilon for distance and cross-product comparisons to avoid issues with floating-point arithmetic.

## 9. References
*   Barber, C. B., Dobkin, D. P., & Huhdanpaa, H. (1996). "The Quickhull Algorithm for Convex Hulls". ACM Transactions on Mathematical Software (TOMS).
*   Eddy, W. F. (1977). "A New Convex Hull Algorithm for Planar Sets". ACM Transactions on Mathematical Software (TOMS).
*   Bykat, A. (1978). "Convex Hull of a Finite Set of Points in Two Dimensions". Information Processing Letters.
*   [Wikipedia: Quickhull](https://en.wikipedia.org/wiki/Quickhull_algorithm)
