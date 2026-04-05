# Fréchet Distance

## 1. Overview
The Fréchet distance is a measure of similarity between two curves (trajectories) that takes into account the location and ordering of points along the curves. It is often described using the **dog-leash analogy**: imagine a person walking along one curve and a dog walking along the other. The Fréchet distance is the minimum length of a leash needed to connect the two as they traverse their respective paths from start to finish. It is a more robust measure of curve similarity than the Hausdorff distance because it respects the parameterization of the curves.

## 2. Definitions
*   **Discrete Fréchet Distance**: A version calculated for polygonal chains (sequences of points).
*   **Free Space Diagram**: A 2D diagram representing the pairs of points on two curves that are within distance $\epsilon$.
*   **Dog-Leash Analogy**: Both subjects can vary their speeds but cannot move backward.
*   **Hausdorff Distance**: A simpler metric that only considers the distance from a point on one set to the closest point on the other, without regard for ordering.

## 3. Theory
For two curves $P$ and $Q$ of lengths $n$ and $m$, the discrete Fréchet distance $d_F(P, Q)$ is the minimum cost of a "coupling" between the two sequences. This is typically solved using **dynamic programming**.

1.  Let $dp[i][j]$ be the Fréchet distance between the prefix $P[0 \dots i]$ and $Q[0 \dots j]$.
2.  The base case is $dp[0][0] = dist(P[0], Q[0])$.
3.  The recurrence relation is:
    $dp[i][j] = \max(dist(P[i], Q[j]), \min(dp[i-1][j], dp[i][j-1], dp[i-1][j-1]))$.
4.  The final result is $dp[n-1][m-1]$.

For continuous curves, the problem is solved by searching for a "monotone path" from $(0,0)$ to $(1,1)$ in the **Free Space Diagram**.

## 4. Pseudo code
```python
function DiscreteFrechet(P, Q):
    n = len(P)
    m = len(Q)
    dp = array[n][m] initialized to -1
    
    # Initialize corners and boundaries
    dp[0][0] = Distance(P[0], Q[0])
    for i in range(1, n):
        dp[i][0] = max(dp[i-1][0], Distance(P[i], Q[0]))
    for j in range(1, m):
        dp[0][j] = max(dp[0][j-1], Distance(P[0], Q[j]))
        
    # Fill DP table
    for i in range(1, n):
        for j in range(1, m):
            cost = Distance(P[i], Q[j])
            dp[i][j] = max(cost, min(dp[i-1][j], 
                                     dp[i-1][j-1], 
                                     dp[i][j-1]))
            
    return dp[n-1][m-1]
```

## 5. Parameters Selections
*   **Distance Metric**: Euclidean distance is standard, but Manhattan or Chebyshev distances can also be used.
*   **Normalization**: Curves should be normalized for scale or rotation if required by the application.

## 6. Complexity
*   **Time Complexity**: $O(n \cdot m)$ for curves with $n$ and $m$ vertices.
*   **Space Complexity**: $O(n \cdot m)$ to store the DP table.

## 7. Usages
*   **Trajectory Analysis**: Comparing the paths taken by animals, vehicles, or sports players.
*   **Handwriting Recognition**: Comparing a drawn stroke to a template of letters.
*   **Speech Recognition**: Time-aligning two audio signals (Dynamic Time Warping is a similar concept).
*   **Bioinformatics**: Comparing the backbones of proteins or the shapes of molecules.
*   **Computer Vision**: Shape matching for object tracking.

## 8. Testing methods and Edge cases
*   **Identical Curves**: The distance should be 0.
*   **Reversed Curves**: If one curve is the reverse of the other, the distance should be large (unlike Hausdorff distance).
*   **Different Sampling Rates**: Test curves where one has many more vertices than the other but covers the same path.
*   **Large Deviations**: A single outlier point in one curve should correctly increase the Fréchet distance.
*   **Looping Curves**: Verify that the algorithm handles self-intersecting paths correctly.

## 9. References
*   Fréchet, M. (1906). "Sur quelques points du calcul fonctionnel". Rendiconti del Circolo Matematico di Palermo.
*   Alt, H., & Godau, M. (1995). "Computing the Fréchet distance between two polygonal curves". International Journal of Computational Geometry & Applications.
*   Eiter, T., & Mannila, H. (1994). "Computing discrete Fréchet distance". Technical Report.
*   Wikipedia: [Fréchet distance](https://en.wikipedia.org/wiki/Fr%C3%A9chet_distance)
