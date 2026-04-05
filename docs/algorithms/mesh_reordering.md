# Mesh Reordering (Reverse Cuthill-McKee)

## 1. Overview
Mesh reordering is the process of permuting the indices of the vertices (and faces) of a mesh to improve the performance of numerical solvers and data access patterns. The most common objective is to minimize the **bandwidth** of the sparse matrices derived from the mesh (like the Laplacian). Reducing the bandwidth ensures that non-zero entries are clustered close to the main diagonal, leading to faster computations and more efficient CPU cache usage.

## 2. Definitions
*   **Bandwidth**: For a matrix $A$, the bandwidth is the maximum value of $|i - j|$ such that $A_{ij} \ne 0$.
*   **Permutation ($P$)**: A mapping that reassigns each vertex index $i$ to a new index $j$.
*   **Profile**: The total number of zeros within the band of the matrix; smaller profiles are generally better.
*   **Adjacency Graph**: The graph where vertices of the mesh are nodes and edges represent connections between them.

## 3. Theory
The most widely used reordering technique is the **Reverse Cuthill-McKee (RCM)** algorithm. It is a refinement of a breadth-first search (BFS) that carefully chooses the starting node and the order of neighbors. 

1.  Find a "pseudo-peripheral" vertex (one that is far from other vertices, often by using a heuristic).
2.  Perform a BFS starting from this vertex.
3.  In each step of the BFS, sort the neighbors by their degree (number of connections) in ascending order.
4.  Once all vertices are visited, reverse the resulting permutation. Reversing is key because it significantly reduces the matrix profile compared to the standard CM order.

## 4. Pseudo code
```python
function RCMReorder(mesh):
    # 1. Choose a starting vertex v with low degree
    v = FindPseudoPeripheralVertex(mesh)
    
    # 2. Standard Cuthill-McKee (BFS)
    R = [v]
    visited = {v}
    
    for current_v in R:
        neighbors = GetNeighbors(current_v, mesh)
        # Sort neighbors by degree
        sorted_neighbors = sorted([n for n in neighbors if n not in visited],
                                  key=lambda n: len(GetNeighbors(n, mesh)))
        
        for n in sorted_neighbors:
            R.append(n)
            visited.add(n)
            
    # 3. Reverse the order
    return list(reversed(R))
```

## 5. Parameters Selections
*   **Starting Vertex**: The choice of the first vertex is critical. A bad starting point leads to high bandwidth. Heuristics like the Gibbs-Poole-Stockmeyer (GPS) algorithm are often used to find a good starting point.
*   **Metric**: While bandwidth reduction is the most common goal, other orderings (like Nested Dissection) are better for parallel solvers or multifrontal methods.

## 6. Complexity
*   **Time Complexity**: $O(V \cdot \Delta \log \Delta)$, where $V$ is vertices and $\Delta$ is average degree. Since $\Delta \approx 6$ for meshes, this is essentially $O(V)$.
*   **Space Complexity**: $O(V + E)$ to store the adjacency list and the visit status.

## 7. Usages
*   **Sparse Linear Solvers**: Essential preprocessing step for Cholesky or LU factorization of Laplacian systems.
*   **FEM Simulations**: Reducing memory access time and improving cache hit rates in structural or fluid simulations.
*   **Data Compression**: Reordered meshes often have more predictable connectivity, allowing for better compression (e.g., in the PLY or OBJ formats).
*   **Rendering**: Improving the vertex cache hit rate during triangle strip or fan rendering.

## 8. Testing methods and Edge cases
*   **Bandwidth Calculation**: Compare the bandwidth of the Laplacian matrix before and after reordering. A successful RCM should show a significant reduction.
*   **Graph with Disconnected Components**: The algorithm must be applied to each component separately and concatenated.
*   **Highly Regular Mesh**: A perfect grid should be reordered into a diagonal-like pattern.
*   **Very Large Mesh**: Ensure the algorithm handles millions of vertices without excessive memory overhead.
*   **Degenerate Mesh**: Test on meshes with very high-valence vertices (where bandwidth reduction is harder).

## 9. References
*   Cuthill, E., & McKee, J. (1969). "Reducing the bandwidth of sparse symmetric matrices". ACM National Conference.
*   George, A. (1971). "Computer implementation of the finite element method". Stanford Technical Report.
*   Liu, W. H., & Sherman, A. H. (1976). "Comparative analysis of the Cuthill-McKee and the reverse Cuthill-McKee algorithms for sparse matrices". SIAM Journal on Numerical Analysis.
*   Wikipedia: [Cuthill-McKee algorithm](https://en.wikipedia.org/wiki/Cuthill%E2%80%93McKee_algorithm)
