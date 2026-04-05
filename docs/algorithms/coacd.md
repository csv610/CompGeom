# Approximate Convex Decomposition (CoACD)

## 1. Overview
Approximate Convex Decomposition (ACD) is the process of partitioning a 3D surface mesh into a set of nearly convex parts. Unlike exact convex decomposition, which can produce an enormous number of tiny, thin pieces for complex organic shapes, ACD allows for a controllable level of "concavity tolerance." This results in a small number of visually meaningful parts that are easy to handle in physics engines and motion planning. CoACD (Collision-oriented ACD) is a modern, state-of-the-art implementation that prioritizes accuracy and performance for collision detection.

## 2. Definitions
*   **Concavity**: A measure of how much a shape deviates from being convex. It is often measured as the maximum distance from the surface to its convex hull.
*   **Decomposition**: A collection of parts whose union matches the original shape and whose interiors are disjoint.
*   **Cutting Plane**: A plane used to split a non-convex part into two smaller, more convex parts.

## 3. Theory
CoACD operates by recursively splitting the mesh using a **best-fit cutting plane**.
1.  **Voxelization**: The input mesh is first converted into a high-resolution voxel grid to simplify the geometry and handle potential topological defects (like holes or self-intersections).
2.  **Concavity Estimation**: For each part, the maximum distance from the surface to its convex hull is calculated. If this distance is below the `threshold`, the part is accepted as "approximately convex."
3.  **Plane Selection**: If a part is too concave, the algorithm searches for a cutting plane that minimizes the sum of concavities of the two resulting parts. This is often done by sampling candidate planes from the mesh's dual graph or using a manifold-aware search.
4.  **Merging**: After decomposition, adjacent parts that are nearly convex together can be merged to further reduce the total part count.

## 4. Pseudo code
```python
function CoACD(mesh, threshold, max_parts):
    # 1. Preprocess: Voxelize and cleanup
    v_mesh = Voxelize(mesh)
    parts = [v_mesh]
    result = []
    
    # 2. Recursive Splitting
    while parts:
        current = parts.pop()
        concavity = CalculateConcavity(current)
        
        if concavity <= threshold or len(result) >= max_parts:
            result.append(current)
        else:
            # Find best plane by sampling
            best_plane = FindBestCuttingPlane(current)
            P1, P2 = Split(current, best_plane)
            parts.extend([P1, P2])
            
    # 3. Postprocess: Merge and remesh
    final_parts = MergeSmallParts(result, threshold)
    return MapToOriginalSurface(final_parts, mesh)
```

## 5. Parameters Selections
*   **Concavity Threshold**: The most important parameter. A smaller threshold (e.g., 0.01) produces many accurate parts; a larger threshold (e.g., 0.1) produces a few coarse parts.
*   **Resolution**: The voxel grid resolution (e.g., 50–100 voxels per side). Higher resolution is slower but more accurate.
*   **Max Parts**: A hard limit on the total number of pieces to prevent excessive fragmentation.

## 6. Complexity
*   **Time Complexity**: $O(K \cdot N \log N)$ where $N$ is the number of voxels/vertices and $K$ is the number of resulting parts. The plane search is the most expensive step.
*   **Space Complexity**: $O(N)$ to store the voxel grid and the sub-meshes.

## 7. Usages
*   **Physics Simulation (Collision Shapes)**: Modern engines like PhysX, Bullet, and Havok work much faster with a set of convex hulls than with a single complex triangle mesh.
*   **Robotics**: Path planning for grippers or mobile robots, where obstacles are simplified into convex hulls for fast distance queries.
*   **Computer Vision**: Segmenting a complex scanned object into its functional components (e.g., a chair into legs, seat, and back).
*   **Animation**: Generating ragdoll physics rigs for characters.

## 8. Testing methods and Edge cases
*   **Perfectly Convex Mesh**: The algorithm should return the original mesh as a single part.
*   **Non-Manifold Geometry**: Verify that the voxelization step correctly "heals" the mesh.
*   **Sharp Spikes**: These create high local concavity; ensure the threshold correctly identifies them.
*   **Thin Structures**: Very thin regions (like a piece of paper) can be tricky for voxelization; check for "leaking" or vanishing parts.
*   **Holes**: Ensure the decomposition doesn't try to "fill" holes unless intended.

## 9. References
*   Wei, X., Liu, J., & Wang, J. (2022). "CoACD: Collision-oriented Approximate Convex Decomposition". SIGGRAPH.
*   Mamou, K., & Ghorbel, F. (2009). "A Simple and Efficient Approach for 3D Mesh Approximate Convex Decomposition". SEGEP.
*   Lien, J. M., & Amato, N. M. (2007). "Approximate Convex Decomposition of Polyhedra". ACM TOG.
*   [GitHub: CoACD repository](https://github.com/Sarah-Wei/CoACD)
