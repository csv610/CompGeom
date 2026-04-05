# Mesh Refinement (Subdivision)

## 1. Overview
Mesh refinement is the process of increasing the resolution of a mesh by subdividing its elements (faces and edges) into smaller ones. The goal is to improve the mesh's quality, accuracy for numerical simulations, or visual smoothness. Refinement can be **global** (applied to the entire mesh) or **local** (applied only to specific regions of interest). Common algorithms include Loop subdivision (for triangles) and Catmull-Clark subdivision (for quads).

## 2. Definitions
*   **Subdivision**: Splitting an existing face into multiple smaller faces.
*   **Edge Split**: Inserting a new vertex at the midpoint of an edge and splitting the edge into two.
*   **Face Split**: Connecting a new vertex at the centroid of a face to its original vertices.
*   **Adaptive Refinement**: Refinement that occurs only where a specific error metric exceeds a threshold.
*   **Stencil**: A weighted average formula used to determine the position of new and original vertices after subdivision.

## 3. Theory
Most refinement schemes follow a two-step process:
1.  **Topological Split**: The mesh connectivity is modified to create more faces (e.g., 1-to-4 triangle split).
2.  **Smoothing (Geometric Update)**: The positions of the new and existing vertices are adjusted based on their neighbors to achieve a specific level of smoothness (e.g., $C^1$ or $C^2$ continuity).

For example, in **Loop Subdivision**:
*   Each triangle is split into four smaller triangles.
*   New "edge vertices" are positioned using a weighted average of the endpoints and the opposite vertices of the two incident faces.
*   Original "even vertices" are repositioned based on their neighbors to maintain surface smoothness.

## 4. Pseudo code
### Simple 1-to-4 Triangle Refinement
```python
function RefineMesh(mesh):
    new_vertices = mesh.vertices[:]
    new_faces = []
    
    # Map from original edge to its new midpoint vertex ID
    edge_midpoints = {}
    
    # 1. Create new vertices at every edge midpoint
    for edge in mesh.edges:
        v1, v2 = edge
        mid_p = (mesh.vertices[v1] + mesh.vertices[v2]) / 2.0
        edge_midpoints[tuple(sorted(edge))] = len(new_vertices)
        new_vertices.append(mid_p)
        
    # 2. Create four new triangles for every original face
    for face in mesh.faces:
        v1, v2, v3 = face
        m1 = edge_midpoints[tuple(sorted((v1, v2)))]
        m2 = edge_midpoints[tuple(sorted((v2, v3)))]
        m3 = edge_midpoints[tuple(sorted((v3, v1)))]
        
        # The 4 sub-triangles
        new_faces.append((v1, m1, m3))
        new_faces.append((v2, m2, m1))
        new_faces.append((v3, m3, m2))
        new_faces.append((m1, m2, m3))
        
    return Mesh(new_vertices, new_faces)
```

## 5. Parameters Selections
*   **Refinement Level**: The number of iterations. Each iteration of 1-to-4 split quadruples the number of faces.
*   **Metric**: For adaptive refinement, common metrics include curvature, gradient of a simulated field (e.g., stress or temperature), or edge length.

## 6. Complexity
*   **Time Complexity**: $O(F \cdot 4^k)$ where $F$ is the original face count and $k$ is the refinement level.
*   **Space Complexity**: $O(F \cdot 4^k)$ to store the refined mesh.

## 7. Usages
*   **Computer Graphics**: Generating high-fidelity models from low-poly base meshes (e.g., characters in movies or games).
*   **Finite Element Method (FEM)**: Improving solution accuracy in regions with high stress or fluid turbulence.
*   **3D Printing**: Increasing the resolution of a mesh to ensure smooth curved surfaces after slicing.
*   **Terrain Modeling**: Adding detail to a coarse elevation grid where the landscape is complex.
*   **Surface Reconstruction**: Improving the density of a mesh fitted to a sparse point cloud.

## 8. Testing methods and Edge cases
*   **Consistency**: Verify that the refined mesh occupies the exact same volume as the original (for linear refinement).
*   **Manifold Property**: Ensure refinement doesn't introduce non-manifold edges or vertices.
*   **Boundaries**: Verify that boundary edges are correctly split and handled (often boundary rules are different from interior rules).
*   **Watertightness**: Check that no gaps are introduced between adjacent sub-triangles.
*   **High Valence**: Test on meshes with "poles" (vertices with many incident edges).

## 9. References
*   Loop, C. (1987). "Smooth subdivision surfaces based on triangle meshes". Master's thesis, University of Utah.
*   Catmull, E., & Clark, J. (1978). "Recursively generated B-spline surfaces on arbitrary topological meshes". Computer-Aided Design.
*   Botsch, M., Kobbelt, L., Pauly, M., Alliez, P., & Lévy, B. (2010). "Polygon Mesh Processing". CRC Press.
*   Wikipedia: [Subdivision surface](https://en.wikipedia.org/wiki/Subdivision_surface)
