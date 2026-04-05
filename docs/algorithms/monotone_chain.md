# Monotone Chain (Convex Hull)

## 1. Overview
The Monotone Chain algorithm (also known as Andrew's algorithm) is a method for computing the convex hull of a finite set of points in the plane. It was first described by A. M. Andrew in 1979. It is generally faster than the Graham scan because it avoids the calculation of polar angles and trigonometric functions, relying solely on sorting and cross-product tests.

## 2. Definitions
*   **Convex Hull**: The smallest convex set containing all given points.
*   **Upper Hull**: The portion of the convex hull consisting of the vertices between the leftmost and rightmost points, starting from the leftmost point and going clockwise along the top.
*   **Lower Hull**: The portion of the convex hull consisting of the vertices between the leftmost and rightmost points, starting from the leftmost point and going counter-clockwise along the bottom.
*   **Orientation Test**: A 2D cross-product calculation to determine if three points form a left turn, right turn, or are collinear.

## 3. Theory
The algorithm takes advantage of the fact that the convex hull can be split into upper and lower chains. By sorting the points lexicographically (first by x-coordinate, then by y-coordinate), we can build the lower hull by scanning the sorted points from left to right. A similar process (scanning either the reversed points or right-to-left) yields the upper hull. For each chain, the algorithm maintains a stack and removes the last point if it doesn't form a "valid" turn relative to the previous points.

## 4. Pseudo code
```python
function MonotoneChain(points):
    if len(points) <= 2: return points
    
    # 1. Sort points lexicographically (x then y)
    points.sort()
    
    # 2. Build lower hull
    lower = []
    for p in points:
        while len(lower) >= 2 and cross_product(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)
        
    # 3. Build upper hull
    upper = []
    for p in reversed(points):
        while len(upper) >= 2 and cross_product(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)
        
    # 4. Concatenate (removing the last points of each hull as they are duplicates)
    return lower[:-1] + upper[:-1]
```

## 5. Parameters Selections
*   **Input**: A list of `Point2D` objects.
*   **Sorting Key**: Points are sorted primarily by their x-coordinate and secondarily by their y-coordinate.

## 6. Complexity
*   **Time Complexity**: $O(n \log n)$ due to sorting. The construction phase is strictly $O(n)$, as each point is added and removed at most once for each hull.
*   **Space Complexity**: $O(n)$ to hold the sorted points and the resulting hull.

## 7. Usages
*   Standard 2D convex hull calculation in many libraries (e.g., SciPy as a fallback).
*   Calculating the area of a set of points.
*   Simplifying complex polygons.
*   GIS and map boundary creation.

## 8. Testing methods and Edge cases
*   **Vertical Lines**: Points with the same x-coordinate but different y-coordinates.
*   **Collinear Points**: Handled by the `>= 2` and `cross_product <= 0` conditions.
*   **Identical Points**: Lexicographical sort handles duplicates naturally.
*   **Small Sets**: Sets of 0, 1, or 2 points return early.
*   **Closed Hulls**: Ensure the first point and last point of each chain match up correctly at the extremities.

## 9. References
*   Andrew, A. M. (1979). "Another Efficient Algorithm for Convex Hulls in Two Dimensions". Information Processing Letters.
*   Preparata, F. P., & Shamos, M. I. (1985). "Computational Geometry: An Introduction". Springer-Verlag.
*   [Wikipedia: Monotone chain](https://en.wikipedia.org/wiki/Monotone_chain_algorithm)
