# Convex Partitioning (Optimal)

## 1. Overview
Convex partitioning is the problem of dividing a non-convex (concave) polygon into the **minimum possible number** of convex sub-polygons. While a simple decomposition (like triangulation) results in $n-2$ convex parts, an optimal partition typically results in significantly fewer. This problem is solvable in polynomial time for simple polygons, making it a powerful tool for geometric simplification.

## 2. Definitions
*   **Simple Polygon**: A polygon with no holes and no self-intersections.
*   **Concave (Reflex) Vertex**: A vertex where the internal angle is greater than $180^\circ$. These are the "source" of non-convexity.
*   **Optimal Partition**: A decomposition into $k$ convex parts where $k$ is minimized.
*   **Diagonal**: A segment connecting two vertices that lies entirely within the polygon.

## 3. Theory
The minimum number of convex parts is determined by how reflex vertices are "resolved" by diagonals. Each reflex vertex must be incident to at least one diagonal that splits its reflex angle.

The **Keil-Snoeyink algorithm** uses **dynamic programming** to find the optimal partition of a simple polygon in $O(n^3)$ time (or $O(r^2 n)$ where $r$ is the number of reflex vertices).
1.  Define $DP[i][j]$ as the minimum number of convex parts in the sub-polygon formed by vertices $V_i, \dots, V_j$ and the diagonal $V_i V_j$.
2.  The algorithm systematically builds up solutions for larger sub-polygons by combining solutions for smaller ones and checking if the resulting combination is convex.
3.  The optimal solution handles cases where multiple reflex vertices are resolved by a single diagonal.

## 4. Pseudo code
```python
function MinimumConvexPartition(polygon):
    n = len(polygon.vertices)
    # 1. Identify reflex vertices
    reflex = [v for v in polygon if IsReflex(v)]
    if not reflex: return [polygon]
    
    # 2. DP Table
    # dp[i][j] = min parts for range (i, j)
    # weights = additional info to handle shared diagonals
    dp = array[n][n]
    
    # 3. Dynamic Programming Loop
    for length in range(2, n):
        for i in range(n - length):
            j = i + length
            if not IsDiagonal(i, j, polygon):
                dp[i][j] = infinity
                continue
                
            # Try all intermediate points k
            dp[i][j] = min(dp[i][k] + dp[k][j] for k in range(i+1, j))
            
            # Special logic to check if diagonal (i, j) 
            # resolves reflex vertices at i or j
            if ResolvesReflex(i, j):
                dp[i][j] -= 1
                
    return ExtractPartition(dp, polygon)
```

## 5. Parameters Selections
*   **Polygon Type**: This optimal algorithm is for **simple polygons**. For polygons with holes, the problem is NP-hard.
*   **Goal**: This specifically minimizes the number of **parts**. Other algorithms might minimize the **total length** of diagonals (Minimum Weight Convex Partition).

## 6. Complexity
*   **Time Complexity**: $O(n^3)$ for the general dynamic programming approach. More optimized versions can reach $O(r^2 n)$.
*   **Space Complexity**: $O(n^2)$ to store the DP table.

## 7. Usages
*   **Path Planning**: Breaking a complex floor plan into the fewest convex "rooms" to simplify robot navigation.
*   **Computer Vision**: Representing a complex silhouette as a small number of convex components for shape matching.
*   **Physics Engines**: Reducing the number of primitives needed for collision detection while maintaining accuracy.
*   **Pattern Recognition**: Identifying structural features in complex polygonal datasets.

## 8. Testing methods and Edge cases
*   **Convex Polygon**: Should return the original polygon (1 part).
*   **Star Polygon**: An optimal partition might be smaller than the number of reflex vertices.
*   **"C" Shape**: Should be split into 3 convex parts optimally.
*   **"L" Shape**: Should be split into 2 parts.
*   **Numerical Precision**: Correctness of `IsDiagonal` and `IsReflex` is critical.
*   **Holes**: Verify the algorithm correctly identifies that holes make the optimal solution much harder.

## 9. References
*   Keil, J. M., & Snoeyink, J. S. (2002). "On the time complexity of optimal convex polygon partitioning". Computational Geometry.
*   Hertel, S., & Mehlhorn, K. (1983). "Fast triangulation of simple polygons". FCT.
*   Chazelle, B., & Dobkin, D. P. (1985). "Optimal convex decompositions". Computational Geometry.
*   Wikipedia: [Convex polygon](https://en.wikipedia.org/wiki/Convex_polygon)
