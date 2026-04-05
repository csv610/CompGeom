# Mesh Connected Components

## 1. Overview
Finding the connected components of a mesh is the process of partitioning the mesh into sets of faces or vertices that are reachable from each other through edge connectivity. A single 3D file often contains multiple disjoint geometric objects (e.g., a table and four separate chairs). Identifying these components is a standard preprocessing step for mesh analysis, repair, and selective editing.

## 2. Definitions
*   **Connected Component**: A maximal subgraph where any two nodes are connected by a path.
*   **Adjacency**: In a mesh, two faces are adjacent if they share an edge. Two vertices are adjacent if they share an edge.
*   **Traversal**: The process of visiting all reachable elements in a graph starting from a seed point.

## 3. Theory
The problem of finding connected components in a mesh is equivalent to finding the connected components of its **dual graph** (where nodes are faces) or its **primal graph** (where nodes are vertices).

Standard graph traversal algorithms like **Breadth-First Search (BFS)** or **Depth-First Search (DFS)** are used:
1.  Initialize a set of unvisited faces.
2.  While there are unvisited faces:
    *   Pick an unvisited face as a "seed."
    *   Start a new component.
    *   Perform a BFS/DFS to find all faces reachable from the seed via shared edges.
    *   Mark all reached faces as visited and add them to the current component.

For manifold meshes, face-connectivity is usually sufficient. For non-manifold or point cloud data, vertex-connectivity might be required.

## 4. Pseudo code
```python
function FindMeshComponents(mesh):
    unvisited = set(range(num_faces))
    components = []
    
    while unvisited:
        # 1. Start a new component with a seed
        seed = unvisited.pop()
        current_component = [seed]
        queue = [seed]
        
        # 2. Traverse all reachable faces
        while queue:
            f = queue.pop(0)
            # Find neighbors sharing an edge
            for neighbor in GetAdjacentFaces(f, mesh):
                if neighbor in unvisited:
                    unvisited.remove(neighbor)
                    current_component.append(neighbor)
                    queue.append(neighbor)
                    
        components.append(current_component)
        
    return components
```

## 5. Parameters Selections
*   **Connectivity Type**: **Edge-connectivity** (faces sharing an edge) is standard. **Vertex-connectivity** (faces sharing only a vertex) is "weaker" and will result in fewer, larger components.
*   **Data Structure**: Using a **Half-Edge** structure or an **Adjacency List** makes finding neighbors $O(1)$, leading to optimal performance.

## 6. Complexity
*   **Time Complexity**: $O(F)$ where $F$ is the number of faces, as each face and each adjacency relationship is visited a constant number of times.
*   **Space Complexity**: $O(F)$ to store the visited status and the resulting component lists.

## 7. Usages
*   **Mesh Repair**: Identifying and removing small "floating" noise components (e.g., isolated triangles) from a scan.
*   **Selective Editing**: Selecting an entire object by clicking on a single triangle (e.g., "Select Linked" in Blender).
*   **3D Printing**: Ensuring that a model consists of a single connected "shell" or identifying internal voids.
*   **Rigging and Animation**: Automatically grouping parts of a character (e.g., separating the body from the clothing or eyes).
*   **Physics Simulation**: Treating each connected component as a separate rigid body for collision and dynamics.

## 8. Testing methods and Edge cases
*   **Single Watertight Object**: Should return exactly one component containing all faces.
*   **Disconnected Objects**: Verify that multiple separate objects are correctly identified as distinct components.
*   **Points/Lines**: Ensure the algorithm handles "degenerate" components like isolated vertices or edges.
*   **Non-Manifold Edges**: Verify that connectivity is correctly traced even if three or more faces share an edge.
*   **Large Meshes**: Test performance on meshes with millions of triangles to ensure linear scaling.

## 9. References
*   Hopcroft, J., & Tarjan, R. (1973). "Efficient algorithms for graph manipulation". Communications of the ACM.
*   Botsch, M., Kobbelt, L., Pauly, M., Alliez, P., & Lévy, B. (2010). "Polygon Mesh Processing". CRC Press.
*   Wikipedia: [Connected component (graph theory)](https://en.wikipedia.org/wiki/Connected_component_(graph_theory))
