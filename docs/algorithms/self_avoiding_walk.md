# Self-Avoiding Walk

## 1. Overview
A self-avoiding walk (SAW) is a sequence of moves on a lattice (such as a 2D or 3D grid) that does not visit the same point more than once. Unlike a simple random walk, which can cross its own path, a SAW must satisfy the constraint of self-exclusion. This exclusion makes SAWs significantly more difficult to analyze and simulate, as the "future" path depends on the entire "history" of the walk.

## 2. Definitions
*   **Lattice**: A regular grid of points (e.g., square, hexagonal, cubic).
*   **Length (n)**: The number of steps in the walk.
*   **Connective Constant ($\mu$)**: A constant describing the growth rate of the number of possible SAWs of length $n$.
*   **End-to-End Distance**: The Euclidean distance between the starting point and the final point.

## 3. Theory
The number of simple random walks of length $n$ on a $d$-dimensional lattice is exactly $(2d)^n$. For SAWs, there is no simple formula. The number of SAWs $c_n$ is known to behave as $c_n \sim A \mu^n n^{\gamma-1}$, where $\mu$ depends on the lattice and $\gamma$ is a "universal" exponent that depends only on the dimension.

Generating SAWs is a challenge due to **attrition**: if you build a walk step-by-step randomly, you often get "trapped" where all neighboring points have already been visited. This leads to several simulation strategies:
1.  **Simple Sampling**: Generate random walks and discard them if they intersect themselves. (Extremely inefficient for large $n$).
2.  **Pivot Algorithm**: Start with a valid SAW and apply a symmetry operation (rotation or reflection) to a portion of the walk. If the result is still self-avoiding, accept it.
3.  **Rosenbluth Method**: A weighted sampling method that avoids immediate self-intersections.

## 4. Pseudo code
### Simple Recursive SAW Generator
```python
function GenerateSAW(path, n, lattice):
    if len(path) == n:
        return path
        
    current = path[-1]
    neighbors = lattice.GetNeighbors(current)
    
    # Shuffle neighbors to explore randomly
    random.shuffle(neighbors)
    
    for neighbor in neighbors:
        if neighbor not in path:
            # 1. Recursive attempt
            result = GenerateSAW(path + [neighbor], n, lattice)
            if result is not None:
                return result
                
    # 2. Dead end (Backtrack)
    return None
```

## 5. Parameters Selections
*   **Lattice Type**: Square (4 neighbors) and Hexagonal (3 neighbors) are common in 2D.
*   **Algorithm**: Use the **Pivot Algorithm** for generating very long SAWs (thousands of steps) as it is much faster than simple recursion or sampling.

## 6. Complexity
*   **Simple Recursion**: $O(\mu^n)$ in the worst case, as it is an exhaustive search.
*   **Pivot Algorithm**: $O(n)$ or even $O(n^{0.5})$ per successful update, making it feasible for $n \approx 10^6$.
*   **Space Complexity**: $O(n)$ to store the coordinates of the walk.

## 7. Usages
*   **Polymer Physics**: SAWs are the standard model for "linear polymers" in a good solvent, where the exclusion principle represents the "excluded volume" of atoms.
*   **Proteins**: Modeling the backbone of a protein during folding.
*   **Network Science**: Analyzing paths in social or communication networks where nodes shouldn't be repeated.
*   **Material Science**: Studying the distribution of chains in a porous medium.
*   **Combinatorics**: A fundamental problem in counting and probability.

## 8. Testing methods and Edge cases
*   **No Intersections**: Verify that all points in the generated path are unique.
*   **Connectivity**: Ensure each point in the path is a valid neighbor of the previous point on the lattice.
*   **Connective Constant**: Verify that for small $n$, the number of generated SAWs matches known exact counts.
*   **Lattice Boundaries**: If the walk is confined to a box, ensure it handles the boundaries correctly.
*   **Trap Detection**: Verify the algorithm correctly backtracks or terminates when the walker is surrounded by visited points.

## 9. References
*   Madras, N., & Slade, G. (1996). "The Self-Avoiding Walk". Birkhäuser.
*   Flory, P. J. (1953). "Principles of Polymer Chemistry". Cornell University Press.
*   Kennedy, T. (2002). "A faster implementation of the pivot algorithm for self-avoiding walks". Journal of Statistical Physics.
*   Wikipedia: [Self-avoiding walk](https://en.wikipedia.org/wiki/Self-avoiding_walk)
