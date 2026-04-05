# Mesh Boundary Detection

## 1. Overview
Mesh boundary detection is the process of identifying vertices and edges that form the boundary of a surface mesh. In a manifold mesh, every edge is shared by exactly two faces. Boundary edges are those that are part of only one face. Identifying these boundaries is essential for surface parameterization, texture mapping, and mesh editing.

## 2. Definitions
*   **Surface Mesh**: A collection of vertices, edges, and faces that represent a 2D surface in 3D space.
*   **Boundary Edge**: An edge that is incident to exactly one face.
*   **Boundary Vertex**: A vertex that is incident to at least one boundary edge.
*   **Boundary Loop**: A connected cycle of boundary edges and vertices that define a hole or the perimeter of the mesh.

## 3. Theory
The fundamental principle of mesh boundary detection is counting the **face-edge incidence**. For a given mesh $M$:
1.  Iterate through all faces.
2.  For each face, extract its oriented edges (e.g., $(v_1, v_2), (v_2, v_3), (v_3, v_1)$).
3.  Store the occurrence of each edge in a hash map, ignoring the orientation (i.e., $(v_i, v_j)$ is the same as $(v_j, v_i)$).
4.  Edges that appear only **once** in the total count are boundary edges.

Once the boundary edges are identified, they can be chained together by matching endpoints to form one or more boundary loops.

## 4. Pseudo code
```python
function DetectMeshBoundaries(mesh):
    # 1. Count occurrences of each edge
    edge_counts = {}
    for face in mesh.faces:
        for i in range(len(face)):
            v1, v2 = SortedPair(face[i], face[(i+1)%len(face)])
            edge_counts[(v1, v2)] = edge_counts.get((v1, v2), 0) + 1
            
    # 2. Extract boundary edges
    boundary_edges = [edge for edge, count in edge_counts.items() if count == 1]
    
    # 3. Assemble edges into loops
    loops = []
    visited_edges = set()
    for start_edge in boundary_edges:
        if start_edge in visited_edges: continue
        
        current_loop = [start_edge[0], start_edge[1]]
        visited_edges.add(start_edge)
        
        while True:
            # Find the next edge that shares the current loop's end vertex
            next_edge = FindNextBoundaryEdge(current_loop[-1], boundary_edges, visited_edges)
            if next_edge is None or next_edge == start_edge:
                break # Loop is closed or finished
                
            next_v = next_edge[1] if next_edge[0] == current_loop[-1] else next_edge[0]
            current_loop.append(next_v)
            visited_edges.add(next_edge)
            
        loops.append(current_loop)
        
    return loops
```

## 5. Parameters Selections
*   **Mesh Representation**: Using a **Half-Edge** data structure makes boundary detection trivial, as boundary edges are typically stored as "null" half-edges or explicit boundary objects.
*   **Sorting**: When using an indexed face set, sorting the vertex IDs for each edge (e.g., `(min(u,v), max(u,v))`) ensures that the count correctly accounts for both orientations of the same geometric edge.

## 6. Complexity
*   **Time Complexity**: $O(F)$, where $F$ is the number of faces in the mesh. Chaining the loops takes $O(E_{boundary})$.
*   **Space Complexity**: $O(E)$ to store the edge counts.

## 7. Usages
*   **Surface Parameterization (UV Mapping)**: BFF and Harmonic Mapping require the mesh boundary to be identified and mapped to a 2D shape.
*   **Mesh Repair**: Identifying and filling holes in scanned 3D models.
*   **Texture Blending**: Applying effects specifically at the boundaries of different surface materials.
*   **Physical Simulation**: Applying boundary conditions (like fixing a boundary in place) for Finite Element analysis.

## 8. Testing methods and Edge cases
*   **Watertight Mesh**: A perfectly closed mesh (like a sphere) should return zero boundary edges.
*   **Open Sheet**: A mesh like a flat square should return a single boundary loop containing all perimeter edges.
*   **Non-Manifold Edges**: Edges shared by more than two faces (count $> 2$) should be flagged as errors or handled separately.
*   **Duplicate Faces**: Two faces covering the same three vertices will result in edge counts of 2, making them appear "watertight" even if they are isolated.
*   **Multiple Holes**: Verify that each hole is correctly identified as a separate loop.

## 9. References
*   Botsch, M., Kobbelt, L., Pauly, M., Alliez, P., & Lévy, B. (2010). "Polygon Mesh Processing". CRC Press.
*   Guibas, L. J., & Stolfi, J. (1985). "Primitives for the manipulation of general subdivisions". ACM Transactions on Graphics.
*   [Wikipedia: Boundary (topology)](https://en.wikipedia.org/wiki/Boundary_(topology))
