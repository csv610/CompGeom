# Triangle to Quad Conversion

## 1. Overview
Triangle to quad conversion is the process of transforming a triangle-only mesh into a quad-dominant or pure quadrilateral mesh. Quadrilateral meshes are often preferred in computer graphics and numerical simulations (like Finite Element Analysis) because they follow principal curvature directions better and provide more natural coordinate systems for texture mapping and subdivision.

## 2. Definitions
*   **Dual Graph**: A graph where each triangle is a node and edges connect nodes representing triangles that share an edge.
*   **Perfect Matching**: A set of edges in the dual graph such that every node is incident to exactly one edge. In our context, this corresponds to a pairing of every triangle into a quad.
*   **Quad-Dominant Mesh**: A mesh containing mostly quads but some triangles.
*   **Pure Quad Mesh**: A mesh where every face has exactly four vertices.

## 3. Theory
The most common approach to triangle-to-quad conversion is based on **pairing adjacent triangles**. 
1.  Represent the mesh as a dual graph.
2.  Assign a weight to each edge in the dual graph based on the "quality" of the potential quad (e.g., how close it is to a square or a rectangle, flatness, etc.).
3.  Find a maximum weight matching in this graph.
4.  Each matched pair of triangles is merged into a quadrilateral by removing their shared edge.
5.  Unmatched triangles remain as triangles in the final mesh.

To achieve a **pure quad mesh**, more aggressive techniques are needed, such as:
*   **Catmull-Clark Subdivision**: Every triangle is split into three quads by adding a vertex at the centroid and midpoints of edges. This always results in a pure quad mesh but significantly increases the face count.
*   **Q-Morph**: A front-advancing algorithm that builds quads from the boundary inward.

## 4. Pseudo code
### Greedy Triangle Merging
```python
function GreedyTriangleToQuad(mesh):
    # 1. Build dual graph with edge weights
    dual_graph = BuildDualGraph(mesh)
    weights = CalculateQuadQualityWeights(dual_graph, mesh)
    
    # 2. Greedy Matching
    # Sort dual edges by quality
    sorted_pairs = sorted(weights.keys(), key=lambda x: weights[x], reverse=True)
    
    matched_triangles = set()
    quads = []
    
    for T1, T2 in sorted_pairs:
        if T1 not in matched_triangles and T2 not in matched_triangles:
            # Merge T1 and T2
            new_quad = MergeTriangles(T1, T2, mesh)
            quads.append(new_quad)
            matched_triangles.add(T1)
            matched_triangles.add(T2)
            
    # 3. Collect remaining triangles
    remaining_tris = [T for T in mesh.faces if T not in matched_triangles]
    
    return Mesh(mesh.vertices, quads + remaining_tris)
```

## 5. Parameters Selections
*   **Quality Metric**: A common metric is the ratio of the quad's diagonals or the deviation of its internal angles from $90^\circ$.
*   **Matching Algorithm**: Greedy matching is fast; Blossom's algorithm finds the global maximum weight matching but is much slower.

## 6. Complexity
*   **Graph Construction**: $O(F)$ where $F$ is the number of faces.
*   **Greedy Matching**: $O(F \log F)$ for sorting the dual edges.
*   **Blossom Algorithm**: $O(E \cdot V^2)$, which is $O(F^3)$ for meshes.

## 7. Usages
*   **Finite Element Method (FEM)**: Quads are often more accurate for structural and thermal analysis.
*   **Animation**: Quad meshes deform more predictably during character rigging and skinning.
*   **Subdivision Modeling**: Catmull-Clark subdivision is the industry standard for creating smooth surfaces from quad cages.
*   **Texture Mapping**: Providing a more natural UV grid for 2D textures.

## 8. Testing methods and Edge cases
*   **Planar Mesh**: Merging two triangles into a quad should preserve the flatness.
*   **Non-Convex Pairs**: Merging two triangles into a concave quad should be avoided or flagged (using the quality metric).
*   **Singularities**: Identify "extraordinary vertices" (those not shared by 4 quads).
*   **Watertightness**: Ensure no holes are created at the boundaries of merged quads.
*   **Manifoldness**: The merging process must preserve the manifold property of the mesh.

## 9. References
*   Remacle, J. F., et al. (2012). "A Frontal Delaunay Quad Mesh Generator". International Journal for Numerical Methods in Engineering.
*   Owen, S. J. (1998). "A Survey of Unstructured Mesh Generation Technology". IMR.
*   Bommes, D., Lévy, B., Pietroni, N., Puppo, E., Silva, C., Tarini, M., & Zayer, R. (2013). "State of the Art in Quad-Meshing". Eurographics STAR.
*   Wikipedia: [Types of mesh](https://en.wikipedia.org/wiki/Types_of_mesh#Quadrilateral)
