# Mesh Tunnel Loops

## 1. Overview
Mesh tunnel loops (or handle loops) are non-separating cycles on a surface mesh that "wrap around" the handles of the surface. For a surface of genus $g$, there are $2g$ such fundamental loops. Identifying these loops is essential for computational topology, mesh editing (e.g., "closing" a handle), and understanding the global connectivity of complex shapes. Tunnel loops are often computed as part of a **homology basis**.

## 2. Definitions
*   **Handle**: A topological feature equivalent to a bridge or a donut hole.
*   **Tunnel Loop**: A cycle that goes "through" a handle.
*   **Handle Loop**: A cycle that goes "around" a handle (orthogonal to the tunnel loop).
*   **Non-Separating Cycle**: A cycle that, when removed, does not split the surface into two disconnected components.
*   **Homology Basis**: A minimal set of cycles that generate all possible non-contractible loops on the surface.

## 3. Theory
Tunnel and handle loops come in pairs for each handle of a manifold mesh. The most common algorithm for finding them is based on the **Tree-Cotree Decomposition**:
1.  Compute a **Primal Spanning Tree** $T$ of the vertices and edges.
2.  Compute a **Dual Spanning Tree** $T^*$ of the faces and dual edges, using only dual edges whose primal edges are NOT in $T$.
3.  The remaining edges $L = E \setminus (T \cup T^*)$ are the **generator edges**.
4.  Each generator edge $e \in L$ completes exactly one cycle in $T \cup \{e\}$. These cycles form a basis for the first homology group $H_1(M)$.

For a mesh with genus $g$, there will be exactly $2g$ generator edges, each defining one fundamental loop.

## 4. Pseudo code
```python
function FindTunnelLoops(mesh):
    # 1. Primal Spanning Tree
    primal_tree = ComputeSpanningTree(mesh.vertices, mesh.edges)
    
    # 2. Dual Spanning Tree
    # Using dual edges where primal edge is NOT in primal_tree
    candidate_dual_edges = [e_dual(e) for e in mesh.edges if e not in primal_tree]
    dual_tree = ComputeDualSpanningTree(mesh.faces, candidate_dual_edges)
    
    # 3. Identify Generator Edges
    generators = []
    for e in mesh.edges:
        if e not in primal_tree and e_dual(e) not in dual_tree:
            generators.append(e)
            
    # 4. Construct Loops
    loops = []
    for gen_edge in generators:
        # The loop is the path in primal_tree between endpoints of gen_edge 
        # plus the gen_edge itself
        path = primal_tree.GetPath(gen_edge.v1, gen_edge.v2)
        loops.append(path + [gen_edge])
        
    return loops
```

## 5. Parameters Selections
*   **Weighting**: Using edge lengths as weights in the spanning tree (Kruskal's algorithm) ensures that the resulting loops are "short" and follow the geometric features of the handle.
*   **Basis Type**: The tree-cotree method produces a **homology basis**. More advanced algorithms can produce a **canonical basis** (where loops meet at a single vertex) or **greedy optimal basis** (shortest possible loops).

## 6. Complexity
*   **Time Complexity**: $O(E \log E)$ or $O(E \log V)$ for the spanning tree construction.
*   **Space Complexity**: $O(E)$ to store the primal and dual trees.

## 7. Usages
*   **Mesh Simplification**: Removing handles to reduce the genus of a mesh (e.g., making a model "watertight" for 3D printing).
*   **Shape Analysis**: Calculating Betti numbers to distinguish between different topological classes.
*   **Texture Mapping**: Using handle loops as natural boundaries for UV charts.
*   **Animation**: Constraining deformations to preserve the topological structure of a character (e.g., not "merging" fingers).
*   **Medical Imaging**: Identifying and measuring the size of holes or passages in anatomical structures (like blood vessels or lung airways).

## 8. Testing methods and Edge cases
*   **Sphere (Genus-0)**: The algorithm should find zero tunnel loops.
*   **Torus (Genus-1)**: Should find exactly two loops (the "donut" hole and the "tube" wrap).
*   **Double Torus (Genus-2)**: Should find exactly four loops.
*   **Open Mesh (Boundary)**: Loops that wrap around a boundary (hole) should be handled correctly (they are part of the relative homology).
*   **Disconnected Mesh**: The algorithm must be applied to each connected component independently.

## 9. References
*   Erickson, J., & Whittlesey, K. (2005). "Greedy optimal homotopy and homology generators". SODA.
*   Dey, T. K., Sun, J., & Wang, Y. (2010). "Approximating Cycles in a Shortest Homology Basis". Discrete & Computational Geometry.
*   Gu, X., & Yau, S. T. (2008). "Computational Conformal Geometry". International Press.
*   Wikipedia: [Homology (mathematics)](https://en.wikipedia.org/wiki/Homology_(mathematics))
