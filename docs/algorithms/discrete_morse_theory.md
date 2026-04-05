# Discrete Morse Theory

## 1. Overview
Discrete Morse Theory, developed by Robin Forman, is a combinatorial version of the classical Morse theory used to study the topology of a manifold by analyzing the critical points of a smooth function defined on it. In the discrete setting, it provides a powerful framework for simplifying complex simplicial complexes (like meshes) while preserving their fundamental topological properties (homology). It is used for topological data analysis, mesh compression, and identifying "features" like ridges and valleys in geometric data.

## 2. Definitions
*   **Simplicial Complex ($K$)**: A collection of simplices (vertices, edges, faces) such that every face of a simplex is also in $K$.
*   **Discrete Morse Function ($f$)**: A function that assigns a real number to every simplex in $K$ such that the number of "downward" and "upward" neighbors is strictly controlled.
*   **Gradient Vector Field**: A pairing of simplices into "gradient arrows" $( \alpha^p < \beta^{p+1} )$.
*   **Critical Simplex**: A simplex that is not part of any gradient pair. Critical simplices correspond to the topological features (0-dim: components, 1-dim: handles, 2-dim: voids).
*   **Morse Complex**: A reduced complex formed only by the critical simplices and their connectivity.

## 3. Theory
The core idea of Discrete Morse Theory is the **Discrete Gradient Vector Field**. 
1.  A simplex $\alpha^p$ can be paired with an incident simplex $\beta^{p+1}$ of higher dimension.
2.  If every simplex is paired, the complex can be "collapsed" to a single point without changing its homotopy type.
3.  Any simplex that *cannot* be paired is a **critical simplex**.
4.  The number of critical simplices of dimension $p$ (denoted $m_p$) provides an upper bound on the $p$-th Betti number $\beta_p$ (Morse Inequalities): $m_p \ge \beta_p$.

By constructing an appropriate Morse function, one can extract a **1D skeleton** (the Morse-Smale complex) that summarizes the flow and connectivity of a scalar field (like elevation) over a surface.

## 4. Pseudo code
### Greedy Construction of a Discrete Gradient Field
```python
function GreedyGradientField(mesh):
    # 1. Initialize all simplices as unpaired
    unpaired = set(mesh.all_simplices)
    gradient_pairs = []
    critical_simplices = []
    
    # 2. Iteratively pair simplices (simple collapse)
    while unpaired:
        # Pick a simplex alpha with only one unpaired neighbor beta
        alpha = FindSimplexWithOneNeighbor(unpaired)
        
        if alpha is not None:
            beta = GetOnlyNeighbor(alpha, unpaired)
            gradient_pairs.append((alpha, beta))
            unpaired.remove(alpha)
            unpaired.remove(beta)
        else:
            # 3. No simple collapse possible: alpha is critical
            alpha = unpaired.pop()
            critical_simplices.append(alpha)
            
    return gradient_pairs, critical_simplices
```

## 5. Parameters Selections
*   **Initial Function**: The choice of the input scalar field (e.g., height, curvature, or random) determines which geometric features are identified as critical points.
*   **Simplification Threshold**: Small "noise" critical points can be removed by canceling pairs of critical points (e.g., a small hill and a small saddle) using Morse cancellations.

## 6. Complexity
*   **Time Complexity**: $O(N \log N)$ to sort simplices by function value, followed by $O(N)$ for the greedy pairing, where $N$ is the total number of simplices.
*   **Space Complexity**: $O(N)$ to store the simplices and the gradient field.

## 7. Usages
*   **Topological Data Analysis (TDA)**: Computing persistent homology and identifying stable structural features in noisy data.
*   **Mesh Compression**: Reducing a complex mesh to a much smaller Morse complex that has the same topology.
*   **Terrain Analysis**: Automatically identifying peaks (maximums), pits (minimums), and passes (saddles) in geographic maps.
*   **Scientific Visualization**: Constructing Morse-Smale complexes to segment a volume based on the behavior of a physical field (e.g., velocity or pressure).
*   **Feature Extraction**: Detecting ridge and valley lines on 3D models.

## 8. Testing methods and Edge cases
*   **Sphere**: A perfect discrete Morse function on a sphere should yield exactly two critical simplices: one vertex (min) and one face (max).
*   **Torus**: Should yield one vertex, two edges (loops), and one face.
*   **Euler Characteristic**: Verify the Morse-Euler relation: $\sum (-1)^p m_p = \chi$, where $m_p$ is the number of critical $p$-simplices.
*   **Noise Handling**: Test the algorithm on a noisy field to ensure it produces many small critical points, which can then be simplified.
*   **Boundaries**: Ensure the theory correctly accounts for simplices on the boundary of the complex.

## 9. References
*   Forman, R. (1998). "Discrete Morse Theory". Advances in Mathematics.
*   Forman, R. (2002). "A user's guide to discrete Morse theory". Sém. Lothar. Combin.
*   Gyulassy, A., Natarajan, V., Pascucci, V., & Bremer, P. T. (2008). "A Practical Approach to Morse-Smale Complex Computation: Quasi-complexes and Geometric Methods". IEEE TVCG.
*   Wikipedia: [Discrete Morse theory](https://en.wikipedia.org/wiki/Discrete_Morse_theory)
