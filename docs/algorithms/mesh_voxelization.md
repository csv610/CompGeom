# Mesh Voxelization

## 1. Overview
Mesh voxelization is the process of converting a 3D surface mesh (typically composed of triangles) into a volumetric representation called a **voxel grid**. A voxel (volume element) is the 3D equivalent of a pixel. Voxelization is used to simplify complex geometry, perform volumetric analysis, and prepare models for physics simulations or 3D printing. The process can result in a "binary" voxel grid (occupied vs. empty) or a "solid" voxelization (distinguishing interior from exterior).

## 2. Definitions
*   **Voxel**: A unit of volume on a regular 3D grid.
*   **Resolution**: The number of voxels along each axis (e.g., $128 \times 128 \times 128$).
*   **Conservative Voxelization**: A method that ensures a voxel is marked as occupied if any part of the triangle passes through it.
*   **Parity Rule**: A technique for solid voxelization where a voxel's "insideness" is determined by counting intersections of a ray with the mesh boundary.

## 3. Theory
The most common approach to surface voxelization is based on **triangle-box intersection** tests.
1.  Define a 3D grid that encloses the mesh's bounding box.
2.  For each triangle in the mesh:
    *   Determine the range of voxels it might intersect (its AABB in grid coordinates).
    *   For every voxel in that range, perform a rigorous triangle-box intersection test (e.g., using the Akenine-Möller algorithm based on the Separating Axis Theorem).
3.  To perform **solid voxelization** (filling the interior):
    *   After surface voxelization, use a flood-fill algorithm starting from the grid boundaries to identify "outside" voxels.
    *   Everything not reachable from the outside is "inside."
    *   Alternatively, use ray-casting along each grid line and apply the even-odd rule.

## 4. Pseudo code
```python
function VoxelizeMesh(mesh, resolution):
    # 1. Initialize grid
    bbox = mesh.GetBoundingBox()
    voxel_size = max(bbox.size) / resolution
    grid = array[resolution][resolution][resolution] initialized to EMPTY
    
    # 2. Surface Voxelization
    for triangle in mesh.faces:
        # Get grid bounds for this triangle
        min_v = WorldToGrid(triangle.min, bbox, voxel_size)
        max_v = WorldToGrid(triangle.max, bbox, voxel_size)
        
        for x in range(min_v.x, max_v.x + 1):
            for y in range(min_v.y, max_v.y + 1):
                for z in range(min_v.z, max_v.z + 1):
                    voxel_box = GetVoxelBox(x, y, z, bbox, voxel_size)
                    if TriangleBoxIntersect(triangle, voxel_box):
                        grid[x][y][z] = SURFACE
                        
    # 3. Solid Voxelization (Optional)
    FloodFill(grid, start_pos=(0,0,0), target=EMPTY, replacement=OUTSIDE)
    for x, y, z in grid:
        if grid[x][y][z] == EMPTY:
            grid[x][y][z] = INSIDE
            
    return grid
```

## 5. Parameters Selections
*   **Resolution**: Higher resolution captures more detail but increases memory consumption cubically ($O(N^3)$).
*   **Intersection Strategy**: Conservative voxelization is preferred for tasks like collision detection to avoid "gaps" in the surface.

## 6. Complexity
*   **Time Complexity**: $O(F \cdot K^3)$ where $F$ is the face count and $K$ is the local grid size per triangle. For solid filling, $O(N^3)$ where $N$ is the resolution.
*   **Space Complexity**: $O(N^3)$ to store the 3D grid. Sparse representations like **OpenVDB** or **Octrees** can reduce this significantly.

## 7. Usages
*   **3D Printing**: Slicing software voxelizes models to generate toolpaths and infill patterns.
*   **Physics Simulation**: Converting complex meshes into voxels for fluid dynamics (Lattice Boltzmann Method) or smoke simulation.
*   **Collision Detection**: Using a voxel grid as a spatial index for fast intersection queries.
*   **Medical Imaging**: Modeling organs or bones from surface scans for surgical planning.
*   **Game Development**: destructible environments (e.g., Minecraft or Teardown) and GPU-based global illumination.

## 8. Testing methods and Edge cases
*   **Watertightness**: Verify that solid voxelization produces no "leaks" for a closed mesh.
*   **Thin Features**: Ensure triangles thinner than a voxel are still captured (conservative test).
*   **Non-Manifold Mesh**: Test how the solid filler handles meshes with holes (usually results in the entire model being marked as outside).
*   **Numerical Precision**: Triangle-box tests are sensitive to floating-point errors; use robust epsilon values.
*   **Memory Limit**: Check performance and stability at high resolutions (e.g., $1024^3$).

## 9. References
*   Akenine-Möller, T. (2001). "Fast 3D Triangle-Box Overlap Testing". Journal of Graphics Tools.
*   Nooruddin, F. S., & Turk, G. (2003). "Simplification and Repair of Polygonal Models Using Volumetric Techniques". IEEE TVCG.
*   Schwarz, M., & Seidel, H. P. (2010). "Fast Parallel Surface and Solid Voxelization on GPUs". ACM TOG.
*   Wikipedia: [Voxel](https://en.wikipedia.org/wiki/Voxel)
