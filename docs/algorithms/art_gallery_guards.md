# Art Gallery Guard Placement

## 1. Overview
The Art Gallery Problem (AGP) is a classic problem in computational geometry that asks for the minimum number of guards required to monitor every point within a given art gallery (represented as a simple polygon). A guard at a point $P$ can "see" any point $Q$ if the line segment $PQ$ lies entirely within the polygon.

## 2. Definitions
*   **Art Gallery**: A simple polygon $P$ with $n$ vertices.
*   **Visibility**: A point $Q$ is visible from $P$ if $PQ \subset P$.
*   **Guard Set**: A set of points $\{G_1, G_2, \dots, G_k\}$ such that every point in $P$ is visible from at least one $G_i$.
*   **Chvátal's Art Gallery Theorem**: For a simple polygon with $n$ vertices, $\lfloor n/3 \rfloor$ guards are always sufficient and sometimes necessary to guard the polygon.

## 3. Theory
The most common constructive proof for Chvátal's theorem uses **polygon triangulation and 3-coloring**. 
1.  **Triangulate** the polygon into $n-2$ triangles using an algorithm like ear clipping or monotone decomposition.
2.  **3-color** the vertices of the resulting triangulation graph such that no two adjacent vertices share the same color. Since the triangulation graph of a simple polygon is the dual of a tree, it is always 3-colorable.
3.  **Count** the number of vertices for each of the three colors. The color with the minimum count will have at most $\lfloor n/3 \rfloor$ vertices.
4.  **Place** a guard at every vertex of this minimum-count color. Since every triangle in the triangulation must contain all three colors, every triangle is visible from at least one guard.

## 4. Pseudo code
```python
function PlaceGuards(polygon):
    # 1. Triangulate the polygon
    triangles = Triangulate(polygon)
    
    # 2. Build the triangulation graph
    graph = BuildTriangulationGraph(triangles)
    
    # 3. 3-Color the graph (using DFS since it's a chordal graph)
    colors = {v: None for v in polygon.vertices}
    DFS_Coloring(graph, start_vertex, colors)
    
    # 4. Partition vertices by color
    color_groups = [[], [], []]
    for v, c in colors.items():
        color_groups[c].append(v)
        
    # 5. Select the smallest group
    guard_positions = min(color_groups, key=len)
    
    return guard_positions
```

## 5. Parameters Selections
*   **Vertex Placement vs. Point Placement**: Standard AGP places guards on vertices. Placing guards anywhere on the interior (Point Guarding) might reduce the total count in some cases, but the theorem remains the same for worst-case bounds.
*   **Triangulation Algorithm**: The choice of triangulation (ear clipping vs. monotone) doesn't affect the 3-coloring result but does affect performance.

## 6. Complexity
*   **Time Complexity**: $O(n \log n)$ using monotone decomposition for triangulation, followed by $O(n)$ for graph construction and 3-coloring.
*   **Space Complexity**: $O(n)$ to store the triangles and the coloring graph.

## 7. Usages
*   **Physical Security**: Optimizing the placement of cameras or motion sensors in buildings.
*   **Wireless Networking**: Determining the minimum number of Wi-Fi access points or cellular towers to cover a given region.
*   **Robotics**: Path planning for a surveillance robot that needs to maintain visibility of its surroundings.
*   **Environmental Monitoring**: Placing sensors to detect smoke or pollutants in complex indoor spaces.

## 8. Testing methods and Edge cases
*   **Convex Polygons**: $n=3, 4, 5$ all require only 1 guard ($\lfloor 5/3 \rfloor = 1$).
*   **Comb Polygons**: "Comb" shapes (ortho-polygons) reach the upper bound of $\lfloor n/3 \rfloor$.
*   **Star Polygons**: By definition, star polygons only require 1 guard (placed at the kernel).
*   **Orthogonal Polygons**: For polygons where all edges are horizontal or vertical, the bound is tighter: $\lfloor n/4 \rfloor$ guards are sufficient (Hoffman's Theorem).
*   **Holes**: Polygons with holes require significantly more guards, and the problem becomes NP-hard.

## 9. References
*   Chvátal, V. (1975). "A combinatorial theorem in plane geometry". Journal of Combinatorial Theory, Series B.
*   Fisk, S. (1978). "A short proof of Chvátal's watchman theorem". Journal of Combinatorial Theory, Series B.
*   O'Rourke, J. (1987). "Art Gallery Theorems and Algorithms". Oxford University Press.
*   [Wikipedia: Art gallery problem](https://en.wikipedia.org/wiki/Art_gallery_problem)
