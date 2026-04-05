# Manifold Verification

## 1. Overview
Manifold verification is the process of checking whether a 3D surface mesh satisfies the topological constraints of a 2nd-order manifold. A manifold surface is one that "locally looks like a flat plane" at every point. Manifold meshes are highly desirable in geometric modeling because they have well-defined orientations, consistent normals, and are compatible with standard data structures like the half-edge mesh.

## 2. Definitions
*   **Edge Manifold**: An edge is manifold if it is shared by exactly two faces (for a closed surface) or one face (for a boundary edge).
*   **Vertex Manifold**: A vertex is manifold if its surrounding faces form a single, connected "fan" or "disk."
*   **Watertight**: A closed manifold mesh with no holes (all edges have exactly two incident faces).
*   **Euler Characteristic ($\chi$)**: For a manifold mesh with $V$ vertices, $E$ edges, and $F$ faces, $\chi = V - E + F$. For a sphere-like surface, $\chi = 2$.

## 3. Theory
To verify that a mesh is a manifold, we check three primary conditions:
1.  **Edge Condition**: Every edge must be incident to either one or two faces. Edges with three or more incident faces (non-manifold edges) are topologically ambiguous.
2.  **Vertex Condition**: For each vertex, the set of faces sharing that vertex must be edge-connected. If a vertex belongs to two separate "cones" that only touch at the vertex itself, it is non-manifold.
3.  **Face Consistency**: For each edge, the orientation of its two incident faces must be compatible (e.g., if one face uses $(u, v)$, the other must use $(v, u)$).

## 4. Pseudo code
```python
function IsManifold(mesh):
    # 1. Edge Count Check
    edge_faces = GetEdgeFaceMap(mesh)
    for edge, faces in edge_faces.items():
        if len(faces) > 2:
            return False, "Non-manifold edge detected"
            
    # 2. Vertex Connectivity Check
    for vertex in mesh.vertices:
        neighbor_faces = GetFacesSharingVertex(vertex, mesh)
        if not IsConnected(neighbor_faces, vertex):
            return False, "Non-manifold vertex detected"
            
    # 3. Normal Consistency Check
    if not HasConsistentOrientation(mesh):
        return False, "Inconsistent face orientations"
        
    return True, "Mesh is manifold"

function IsConnected(faces, vertex):
    # Check if all faces sharing a vertex form a single connected component
    # through shared edges that are also incident to the vertex
    components = FindFaceComponents(faces, vertex)
    return len(components) == 1
```

## 5. Parameters Selections
*   **Tolerance**: Floating-point precision should be considered when identifying "duplicate" vertices that should have been merged.
*   **Boundary Handling**: A manifold with a boundary is still a manifold; the condition for boundary edges (1 face) and boundary vertices (faces form a single half-disk) must be handled.

## 6. Complexity
*   **Time Complexity**: $O(F)$, where $F$ is the number of faces, to build the edge-face map and check vertex connectivity.
*   **Space Complexity**: $O(E + F)$ to store the connectivity information.

## 7. Usages
*   **3D Printing**: Slicing software requires watertight, manifold meshes to correctly identify "inside" vs. "outside" volumes.
*   **Physical Simulation**: Finite Element Method (FEM) and Fluid Dynamics simulations often fail on non-manifold geometry.
*   **Mesh Boolean Operations**: Algorithms like Union/Intersection are much more robust on manifold meshes.
*   **Surface Parameterization**: Algorithms like BFF or LSCM rely on a consistent half-edge structure, which requires a manifold mesh.

## 8. Testing methods and Edge cases
*   **T-Junctions**: A vertex lying on an edge of another face (without sharing it) is geometrically non-manifold.
*   **Pinch Points**: Two separate mesh components touching at a single vertex.
*   **Self-Intersections**: A mesh can be topologically manifold while still being geometrically self-intersecting (this is usually checked separately).
*   **Isolated Vertices**: Vertices with zero incident faces.
*   **Inconsistent Normals**: A "Mobius strip" style mesh where orientations cannot be made consistent.

## 9. References
*   Guibas, L. J., & Stolfi, J. (1985). "Primitives for the manipulation of general subdivisions". ACM Transactions on Graphics.
*   Botsch, M., Kobbelt, L., Pauly, M., Alliez, P., & Lévy, B. (2010). "Polygon Mesh Processing". CRC Press.
*   [Wikipedia: Manifold](https://en.wikipedia.org/wiki/Manifold)
