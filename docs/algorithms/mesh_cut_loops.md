# Mesh Cut Loops (Cut Graph)

## 1. Overview
Mesh cut loops (or cut graphs) are sets of edges on a surface mesh that, when removed, transform the mesh into a single topological disk (a genus-0 surface with a single boundary). Identifying these loops is a prerequisite for many surface parameterization algorithms (like BFF or LSCM), as these algorithms require the surface to be homeomorphic to a disk before they can flatten it into 2D UV space.

## 2. Definitions
*   **Genus (g)**: The number of "handles" on a surface. A mesh with genus $g$ requires $2g$ non-separating loops to be cut into a disk.
*   **Fundamental Loops**: A basis for the first homology group of the surface; these loops "wrap around" the handles or holes.
*   **Cut Graph**: A set of edges such that the remaining mesh is a topological disk.
*   **Tree-Cotree Decomposition**: A technique for constructing a cut graph using a spanning tree of the primal mesh and a spanning tree of the dual mesh.

## 3. Theory
For a closed manifold mesh with genus $g$, the Euler characteristic is $\chi = V - E + F = 2 - 2g$. A cut graph that reduces this surface to a disk must contain $2g$ independent cycles that meet at a single vertex (forming a "wedge of circles").

A robust method for finding a cut graph is the **Tree-Cotree Decomposition**:
1.  Compute a **Spanning Tree** $T$ of the vertices and edges of the mesh.
2.  Compute a **Dual Spanning Tree** $T^*$ of the faces and dual edges, but only using dual edges whose primal counterparts are NOT in $T$.
3.  The edges that are in neither $T$ nor $T^*$ form the **Cut Graph**.

This algorithm ensures that the cut graph is minimal and that cutting along it results in exactly one connected component with no handles.

## 4. Pseudo code
```python
function FindCutGraph(mesh):
    # 1. Primal Spanning Tree (BFS on vertices)
    primal_tree = ComputeSpanningTree(mesh.vertices, mesh.edges)
    
    # 2. Identify candidate dual edges
    # Dual edges whose primal edge is NOT in the primal tree
    candidate_dual_edges = [e for e in mesh.edges if e not in primal_tree]
    
    # 3. Dual Spanning Tree (BFS on faces)
    # Using only dual edges from the candidate set
    dual_tree = ComputeDualSpanningTree(mesh.faces, candidate_dual_edges)
    
    # 4. Extract Cut Graph
    # Edges that are in neither tree
    cut_graph_edges = []
    for e in mesh.edges:
        if e not in primal_tree and e_dual(e) not in dual_tree:
            cut_graph_edges.append(e)
            
    return cut_graph_edges
```

## 5. Parameters Selections
*   **Root Selection**: The choice of root for the primal and dual trees affects the shape of the cut graph but not its topological property.
*   **Edge Weights**: Using weights (e.g., edge lengths) in the spanning tree calculation (Kruskal's algorithm) can result in "shorter" or more "geometric" cut paths.

## 6. Complexity
*   **Time Complexity**: $O(E \log E)$ or $O(E)$ depending on the spanning tree algorithm used.
*   **Space Complexity**: $O(E)$ to store the primal and dual tree structures.

## 7. Usages
*   **Surface Parameterization (UV Unwrapping)**: Cutting a torus or a complex organic model so it can be laid flat in 2D.
*   **Texture Mapping**: Defining the "seams" of a 3D model where the texture coordinates are discontinuous.
*   **Mesh Morphing**: Aligning the topology of two different meshes before interpolating between them.
*   **Computational Topology**: Calculating the homology or Betti numbers of a surface.
*   **Geometry Compression**: Cutting a mesh into a single spanning triangle strip or a predictable layout.

## 8. Testing methods and Edge cases
*   **Genus-0 Sphere**: The cut graph should be empty (or a single point/edge if a boundary is forced).
*   **Torus (Genus-1)**: The cut graph should consist of two loops (meridian and longitude) meeting at a vertex.
*   **Multiple Components**: Ensure the algorithm handles disconnected parts of the mesh correctly.
*   **Boundary Handling**: If the mesh already has a boundary, the cut graph only needs to "connect" the boundary to the handles.
*   **Watertight Check**: After cutting, the resulting mesh should have exactly one connected component and its Euler characteristic should be 1.

## 9. References
*   Erickson, J., & Whittlesey, K. (2005). "Greedy optimal homotopy and homology generators". SODA.
*   Gu, X., & Yau, S. T. (2002). "Computing conformal structures of surfaces". Communications in Information and Systems.
*   Eppstein, D. (2003). "Dynamic generators of topologically distinct cycles". Proceedings of the 15th Canadian Conference on Computational Geometry.
*   Wikipedia: [Cut graph](https://en.wikipedia.org/wiki/Cut_graph)
