# Mesh Coloring

## 1. Overview
Mesh coloring is the process of assigning labels (colors) to the elements of a mesh (typically vertices or faces) such that no two adjacent elements share the same label. This is a direct application of graph coloring to the connectivity of a mesh. While it is often used for visual aesthetics, its primary technical purpose is to identify independent sets of elements that can be processed in parallel without race conditions.

## 2. Definitions
*   **k-Coloring**: An assignment of $k$ colors to vertices such that adjacent vertices have different colors.
*   **Vertex Graph**: A graph where vertices of the mesh are nodes and edges of the mesh are graph edges.
*   **Dual Graph (Face Graph)**: A graph where each face of the mesh is a node and edges connect faces that share an edge.
*   **Chromatic Number ($\chi(G)$)**: The minimum number of colors needed to color a graph.

## 3. Theory
For a 2D surface mesh (which is essentially a planar or surface-embedded graph), several key theorems apply:
1.  **Four-Color Theorem**: Any planar graph can be colored with at most 4 colors. Since most surface meshes are locally planar, 4 to 6 colors are typically sufficient.
2.  **Brook's Theorem**: The chromatic number is at most the maximum vertex degree $\Delta$, unless the graph is a complete graph or an odd cycle.

The most common algorithm is the **Greedy Coloring** approach:
1.  Iterate through vertices in a specific order.
2.  For the current vertex, check the colors of its already-colored neighbors.
3.  Assign the smallest available color that is not used by any neighbor.

## 4. Pseudo code
```python
function ColorMesh(mesh, strategy="GREEDY"):
    # 1. Initialize colors
    colors = {v: -1 for v in mesh.vertices}
    
    # 2. Sort vertices to improve coloring quality (Optional)
    # Welzl's or Degree-based sorting
    ordered_vertices = SortByDegree(mesh.vertices, descending=True)
    
    # 3. Greedy Coloring
    for v in ordered_vertices:
        neighbor_colors = set()
        for neighbor in GetNeighbors(v, mesh):
            if colors[neighbor] != -1:
                neighbor_colors.add(colors[neighbor])
                
        # Find first available color index
        color = 0
        while color in neighbor_colors:
            color += 1
            
        colors[v] = color
        
    return colors
```

## 5. Parameters Selections
*   **Ordering Strategy**: Sorting vertices by degree (Largest First) often results in fewer total colors than a random ordering.
*   **Saturation Degree (DSATUR)**: A more advanced strategy that colors vertices with the most uniquely colored neighbors first.

## 6. Complexity
*   **Time Complexity**: $O(V \cdot \Delta)$, where $V$ is the number of vertices and $\Delta$ is the average vertex degree (typically $\Delta \approx 6$ for triangular meshes).
*   **Space Complexity**: $O(V)$ to store the assigned color for each vertex.

## 7. Usages
*   **Parallel Computing (GPGPU)**: When performing operations like mesh smoothing (Mean Curvature Flow) on a GPU, vertices of the same color can be updated simultaneously because they don't share data with each other.
*   **Implicit Solvers**: Partitioning the Laplacian matrix into independent blocks for faster parallel solves.
*   **Visualizing Mesh Structure**: Highlighting different regions or patches for debugging.
*   **Texture Mapping**: Assigning different texture atlases to different parts of a mesh to avoid overlaps.

## 8. Testing methods and Edge cases
*   **Adjacency Check**: After coloring, iterate through every edge $(u, v)$ and verify that `color[u] != color[v]`.
*   **Color Count**: Verify that the total number of colors used is reasonably small (e.g., $< 10$ for typical meshes).
*   **Disconnected Components**: Ensure the algorithm handles multiple separate mesh objects correctly.
*   **High-Valence Vertices**: Check performance and color count on meshes with "star" patterns (vertices with many neighbors).
*   **Face Coloring**: Test by applying the same logic to the dual graph (coloring faces instead of vertices).

## 9. References
*   Welsh, D. J. A., & Powell, M. B. (1967). "An upper bound for the chromatic number of a graph and its application to timetabling problems". The Computer Journal.
*   Brélaz, D. (1979). "New methods to color the vertices of a graph". Communications of the ACM.
*   Wikipedia: [Graph coloring](https://en.wikipedia.org/wiki/Graph_coloring)
