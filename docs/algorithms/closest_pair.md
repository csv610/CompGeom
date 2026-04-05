# Closest Pair of Points

## 1. Overview
The closest pair of points problem is a fundamental challenge in computational geometry that involves finding the two points in a set of $n$ points that have the minimum Euclidean distance between them. While a naive brute-force approach takes $O(n^2)$ time, more efficient algorithms exist, including a deterministic $O(n \log n)$ divide-and-conquer approach and a randomized $O(n)$ grid-based approach.

## 2. Definitions
*   **Euclidean Distance**: For two points $P_1(x_1, y_1)$ and $P_2(x_2, y_2)$, the distance $d = \sqrt{(x_2-x_1)^2 + (y_2-y_1)^2}$.
*   **Divide and Conquer (D&C)**: A recursive strategy that breaks the problem into two halves, solves each, and merges the results.
*   **Grid Hashing**: Mapping points to cells of a grid with a fixed side length to perform fast local searches.

## 3. Theory
### Divide and Conquer Approach
The set of points is first sorted by $x$-coordinate and then split into two halves by a vertical line. The minimum distance is recursively found in the left half ($d_L$) and the right half ($d_R$). Let $d = \min(d_L, d_R)$. The global minimum could still be a pair of points where one is in the left half and one is in the right half. To check this, we only need to consider points within a vertical "strip" of width $2d$ centered on the dividing line. 

Within this strip, for any point $P$, we only need to check points $Q$ that are within distance $d$ of $P$. If the strip points are sorted by $y$-coordinate, it can be proven that each point only needs to be compared with a constant number (at most 7) of succeeding points in the sorted list to find a pair closer than $d$.

### Randomized Grid Approach
This approach uses a grid with cell size $d \times d$. Each cell in the grid contains at most one point (if $d$ is the current minimum distance). When a new point is added, we check its own cell and the 8 neighboring cells. If a closer point is found, the minimum distance $d$ is updated, and the grid is rebuilt with the new cell size. In the randomized version, the expected number of rebuilds is $O(\log n)$, leading to an overall expected time of $O(n)$.

## 4. Pseudo code
### Divide and Conquer
```python
function ClosestPair(points_sorted_x, points_sorted_y):
    if len(points_sorted_x) <= 3:
        return BruteForce(points_sorted_x)
        
    # 1. Split points
    mid = len(points_sorted_x) // 2
    left_x = points_sorted_x[:mid]
    right_x = points_sorted_x[mid:]
    
    # 2. Recursive calls
    (d_L, p1_L, p2_L) = ClosestPair(left_x, points_sorted_y_left)
    (d_R, p1_R, p2_R) = ClosestPair(right_x, points_sorted_y_right)
    
    d = min(d_L, d_R)
    best_pair = (p1_L, p2_L) if d_L < d_R else (p1_R, p2_R)
    
    # 3. Check the strip
    strip = [p for p in points_sorted_y if abs(p.x - points_sorted_x[mid].x) < d]
    for i in range(len(strip)):
        for j in range(i + 1, min(i + 8, len(strip))):
            if dist(strip[i], strip[j]) < d:
                d = dist(strip[i], strip[j])
                best_pair = (strip[i], strip[j])
                
    return (d, best_pair)
```

## 5. Parameters Selections
*   **Algorithm Choice**: Use D&C for general-purpose deterministic results. Use Grid-based for massive streaming datasets where $O(n \log n)$ is too slow.
*   **Base Case**: Brute force for $n < 4$ to avoid excessive recursion overhead.

## 6. Complexity
*   **Divide and Conquer**: $O(n \log n)$ time, $O(n)$ space.
*   **Grid-based**: $O(n)$ expected time, $O(n)$ space.

## 7. Usages
*   **Collision Detection**: Finding the two closest objects in a physics simulation.
*   **Cluster Analysis**: Identifying tight groupings of data points.
*   **Air Traffic Control**: Detecting potential collisions between aircraft.
*   **Bioinformatics**: Comparing molecular structures or sequences.

## 8. Testing methods and Edge cases
*   **Identical Points**: Points with the exact same coordinates (distance 0).
*   **Vertical/Horizontal alignment**: Points forming a perfect grid or line.
*   **Large Coordinates**: Precision issues with squared distances ($x^2 + y^2$) for very large $x, y$.
*   **Sparse vs. Dense**: Performance on points scattered far apart vs. points clustered tightly together.
*   **Verification**: Always compare with an $O(n^2)$ brute-force implementation for small inputs during testing.

## 9. References
*   Shamos, M. I., & Hoey, D. (1975). "Closest-point problems". IEEE FOCS.
*   Khuller, S., & Matias, Y. (1995). "A simple randomized sieve algorithm for the closest-pair problem". Information and Computation.
*   Bentley, J. L., & Shamos, M. I. (1976). "Divide-and-conquer in multidimensional space". ACM STOC.
*   Wikipedia: [Closest pair of points problem](https://en.wikipedia.org/wiki/Closest_pair_of_points_problem)
