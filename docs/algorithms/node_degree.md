# Node Degree Calculation

## 1. Overview
Node degree calculation is the process of counting the number of edges incident to each vertex (node) in a graph or mesh. In the context of 3D meshes, vertex degree (often called **valence**) is a key indicator of mesh quality and topological regularity. Vertices with unusual degrees (extraordinary vertices) can cause artifacts in subdivision and smoothing algorithms.

## 2. Definitions
*   **Valence (Degree)**: The number of edges connected to a vertex.
*   **Regular Vertex**: A vertex with the "ideal" degree for its mesh type (degree 6 for triangle meshes, degree 4 for quad meshes).
*   **Extraordinary Vertex (Singularity)**: A vertex with a degree other than the regular degree.
*   **Average Degree**: The sum of all degrees divided by the number of vertices. For a closed triangle mesh, the average degree is exactly 6.

## 3. Theory
The sum of all vertex degrees in a mesh is equal to twice the number of edges: $\sum deg(v_i) = 2E$. This is known as the **Handshaking Lemma**.

For a closed 2-manifold triangle mesh, the average degree is related to the Euler characteristic $\chi$:
$$\bar{d} = 6 - \frac{6\chi}{V}$$
As the number of vertices $V \to \infty$, the average degree approaches 6. 

In a **Half-Edge** data structure, calculating the degree involves "circulating" around the vertex using the `next` and `twin` pointers until the starting half-edge is reached again.

## 4. Pseudo code
### Using an Adjacency List
```python
function CalculateDegrees(mesh):
    # 1. Initialize degree array
    degrees = [0] * num_vertices
    
    # 2. Iterate through all edges
    for v1, v2 in mesh.edges:
        degrees[v1] += 1
        degrees[v2] += 1
        
    return degrees
```

### Using a Half-Edge Structure
```python
function GetVertexDegree(mesh, v):
    count = 0
    start_he = v.halfedge
    curr_he = start_he
    
    while True:
        count += 1
        # Move to next outgoing half-edge
        curr_he = curr_he.twin.next
        if curr_he == start_he:
            break
            
    return count
```

## 5. Parameters Selections
*   **Boundary Handling**: Vertices on the boundary of an open mesh naturally have lower degrees (typically 2 or 3). They should be flagged or handled separately in quality metrics.
*   **Directed vs. Undirected**: For general graphs, degrees are split into **In-Degree** and **Out-Degree**. For standard surface meshes, edges are considered undirected.

## 6. Complexity
*   **Time Complexity**: $O(E)$ to iterate through all edges, or $O(V \cdot \bar{d})$ to circulate around each vertex. Both are linear in the size of the mesh.
*   **Space Complexity**: $O(V)$ to store the degree values.

## 7. Usages
*   **Mesh Quality Analysis**: Identifying regions with poor connectivity that might cause simulation errors.
*   **Subdivision Surfaces**: Stencils for Loop or Catmull-Clark subdivision change based on the vertex degree to maintain smoothness.
*   **Mesh Simplification**: Algorithms like Quadratic Error Metrics (QEM) often prioritize removing vertices based on their degree and geometric impact.
*   **Network Science**: Identifying "hubs" (nodes with very high degrees) in social or infrastructure graphs.
*   **Topology Verification**: Checking if a mesh is "regular" (e.g., all vertices have degree 6).

## 8. Testing methods and Edge cases
*   **Simple Polyhedra**: Verify that all vertices of a cube have degree 3, and all vertices of an icosahedron have degree 5.
*   **Regular Grid**: A flat triangle grid should have interior vertices of degree 6.
*   **Boundary Vertices**: Test on an open square; corner vertices should have degree 2 and edge vertices degree 3.
*   **Non-Manifold Vertices**: Verify the count when multiple "fans" of triangles meet at a single vertex.
*   **Isolated Vertices**: Ensure vertices with zero edges are handled (degree 0).

## 9. References
*   Diestel, R. (2017). "Graph Theory". Springer.
*   Botsch, M., Kobbelt, L., Pauly, M., Alliez, P., & Lévy, B. (2010). "Polygon Mesh Processing". CRC Press.
*   Wikipedia: [Degree (graph theory)](https://en.wikipedia.org/wiki/Degree_(graph_theory))
