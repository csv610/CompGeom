# Chan's Algorithm (Convex Hull)

## 1. Overview
Chan's algorithm is an **output-sensitive** algorithm for computing the convex hull of a set of $n$ points in 2D or 3D. It combines the strengths of Graham scan (or Monotone Chain) and Jarvis march to achieve an optimal $O(n \log h)$ running time, where $h$ is the number of vertices on the convex hull.

## 2. Definitions
*   **Convex Hull:** The smallest convex set that contains all the points.
*   **Output-Sensitive:** An algorithm whose complexity depends on the size of the output.

## 3. Theory
Chan's algorithm partitions the point set into $n/m$ groups of size $m$. It computes the convex hull of each group in $O(m \log m)$ time. Then, it uses a modified Jarvis march to find the global hull by performing binary searches (tangent queries) on the mini-hulls. By iteratively guessing $m = 2^{2^t}$, it reaches the optimal complexity.

## 4. Pseudo code
```python
Algorithm: Chan's Convex Hull
Input: Set of points P
Output: Convex Hull vertices

1. For t = 1, 2, ...:
2.   m = min(2^(2^t), n)
3.   Partition P into groups of size m.
4.   Compute Monotone Chain hull for each group.
5.   Try to find global hull using Jarvis march in m steps:
6.     From current point, find next hull point by tangent query on each mini-hull.
7.   If hull is closed, return it.
```

## 5. Parameters Selections
*   **Group Size (m):** Controlled by the iteration parameter $t$.

## 6. Complexity
*   **Time:** $O(n \log h)$, which is optimal.
*   **Space:** $O(n)$.

## 7. Usages
Implemented in `compgeom.polygon.convex_hull.Chan`. Used for efficient hull calculation when the number of hull vertices is small.

## 8. Testing methods and Edge cases
*   **Testing:** Compare output with Graham Scan or SciPy's Qhull. Verify all original points are inside the hull.
*   **Edge Cases:** Collinear points, coincident points, small point sets ($n < 3$).

## 9. References
*   Chan, T. M. (1996). "Optimal output-sensitive convex hull algorithms in two and three dimensions". Discrete & Computational Geometry.
*   Wikipedia: [Chan's algorithm](https://en.wikipedia.org/wiki/Chan%27s_algorithm)
