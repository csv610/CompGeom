# Mesh Rigidity

## 1. Overview
Mesh rigidity is the study of whether a framework of vertices and edges (a mesh) can be continuously deformed while preserving the lengths of all its edges. A mesh is **rigid** if the only possible motions are rigid body motions (translation and rotation). If it can be deformed in other ways, it is **flexible**. Rigidity analysis is critical for structural engineering, robotics, and molecular biology.

## 2. Definitions
*   **Bar-and-Joint Framework**: A graph where edges represent rigid bars and vertices represent flexible joints.
*   **Rigidity Matrix ($R$)**: A matrix that relates the velocities of vertices to the rates of change of edge lengths.
*   **Infinitesimal Rigidity**: A linear approximation where a mesh is rigid if the only vertex velocities that preserve edge lengths (to first order) are rigid body motions.
*   **Degrees of Freedom (DOF)**: The dimension of the kernel of the rigidity matrix. For a rigid 3D framework, $DOF = 6$ (3 translation + 3 rotation).

## 3. Theory
The rigidity of a mesh is determined by the **Rigidity Matrix** $R$. For each edge $(i, j)$, there is a row in $R$ containing the vector $(P_i - P_j)$ at columns corresponding to $P_i$ and $(P_j - P_i)$ at columns for $P_j$. 

A framework is infinitesimally rigid if the rank of $R$ is $3V - 6$ (in 3D) or $2V - 3$ (in 2D). 
*   If $\text{rank}(R) < 3V - 6$, the mesh has internal mechanisms (it is flexible).
*   If $\text{rank}(R) = 3V - 6$, the mesh is rigid. 
*   If the number of edges $E > 3V - 6$, the mesh is **redundantly rigid** or over-constrained.

**Maxwell's Counting Rule** (Laman's Theorem in 2D) provides a combinatorial necessary condition: a graph must have at least $3V-6$ edges to be rigid in 3D, but this is not sufficient (as the edges might be poorly distributed).

## 4. Pseudo code
```python
function AnalyzeMeshRigidity(mesh):
    V = len(mesh.vertices)
    E = len(mesh.edges)
    
    # 1. Check necessary combinatorial condition
    if E < 3 * V - 6:
        return "Flexible (under-constrained)"
        
    # 2. Build Rigidity Matrix
    # Size E x 3V
    R = SparseMatrix(E, 3 * V)
    for row_idx, edge in enumerate(mesh.edges):
        i, j = edge
        pi = mesh.vertices[i]
        pj = mesh.vertices[j]
        diff = pi - pj
        
        # Fill row with (pi-pj) and (pj-pi)
        R[row_idx, 3*i : 3*i+3] = diff
        R[row_idx, 3*j : 3*j+3] = -diff
        
    # 3. Calculate Rank
    # Use Singular Value Decomposition (SVD) or QR
    rank = CalculateRank(R)
    
    # 4. Interpret Result
    dof = 3 * V - rank
    if dof == 6:
        return "Rigid"
    else:
        return f"Flexible with {dof - 6} internal mechanisms"
```

## 5. Parameters Selections
*   **Numerical Tolerance**: Since rank calculation is sensitive to noise, a threshold based on the machine epsilon or the smallest non-zero singular value must be used.
*   **Generic vs. Specific Position**: A mesh might be rigid in general but flexible in a specific degenerate configuration (e.g., all vertices on a line). Generic rigidity depends only on the graph topology.

## 6. Complexity
*   **Matrix Construction**: $O(E)$.
*   **Rank Calculation**: $O(E \cdot V^2)$ using SVD. For large meshes, sparse solvers or **Pebble Game** algorithms (for combinatorial rigidity) are used.

## 7. Usages
*   **Structural Engineering**: Verifying that a bridge or building truss is stable and won't collapse.
*   **Robotics**: Analyzing the workspace and mobility of parallel manipulators.
*   **Molecular Biology**: Studying the flexibility of protein structures to understand how they bind to other molecules.
*   **Sensor Networks**: Determining if a set of distance measurements is sufficient to uniquely locate all sensors (Localization).
*   **Computer Graphics**: Constraining mesh deformations to be "as-rigid-as-possible" (ARAP) for realistic animation.

## 8. Testing methods and Edge cases
*   **Tetrahedron**: The simplest rigid 3D structure ($V=4, E=6, 3V-6=6$).
*   **Square**: A 2D square with 4 edges is flexible ($V=4, E=4, 2V-3=5$ required); adding a diagonal makes it rigid.
*   **Collinear Vertices**: Verify that the algorithm detects flexibility when vertices are aligned, even if the graph is combinatorially rigid.
*   **Disconnected Mesh**: The rank check should reflect the sum of rigid body motions for each component (6 DOF per component).
*   **Over-constrained Mesh**: Ensure the algorithm handles $E > 3V-6$ correctly.

## 9. References
*   Asimow, L., & Roth, B. (1978). "The rigidity of graphs". Transactions of the American Mathematical Society.
*   Laman, G. (1970). "On graphs and rigidity of plane skeletal structures". Journal of Engineering Mathematics.
*   Connelly, R. (1980). "The rigidity of polyhedra". SIAM Journal on Mathematical Analysis.
*   Wikipedia: [Structural rigidity](https://en.wikipedia.org/wiki/Structural_rigidity)
