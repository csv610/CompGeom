# Delaunay Flips (Edge Flipping)

## 1. Overview
The edge flip algorithm is a local transformation technique used to convert any valid triangulation of a set of points into a **Delaunay triangulation**. It is based on the Lawson Flip Theorem, which states that any two triangulations of the same set of points are connected by a series of edge flips. This process iteratively improves the "quality" of the triangles by ensuring they satisfy the Delaunay (empty circumcircle) property.

## 2. Definitions
*   **Edge Flip**: In a quadrilateral formed by two adjacent triangles, replacing the common diagonal with the other possible diagonal.
*   **Illegal Edge**: An edge is illegal if the vertex of one of its incident triangles lies inside the circumcircle of the other triangle.
*   **Delaunay Property**: A triangulation where no vertex is inside the circumcircle of any triangle.
*   **Angle-Vector**: A vector of all angles in a triangulation, sorted increasingly. Delaunay flips lexicographically maximize this vector (i.e., they make the smallest angles as large as possible).

## 3. Theory
For any interior edge $e$ shared by triangles $T_1 = (A, B, C)$ and $T_2 = (B, C, D)$, we check the **In-Circle** condition for vertex $D$ relative to triangle $ABC$. If $D$ is inside the circumcircle of $ABC$, then the edge $BC$ is illegal. 

Flipping an illegal edge $BC$ produces a new edge $AD$ and two new triangles $ABD$ and $ACD$. It is a proven property that:
1.  Flipping an illegal edge increases the minimum angle of the triangulation.
2.  An illegal edge can only exist if the four vertices form a convex quadrilateral.
3.  By repeatedly flipping illegal edges, the algorithm will eventually converge to the unique Delaunay triangulation (assuming no four points are co-circular).

## 4. Pseudo code
```python
function DelaunayFlip(triangulation):
    # 1. Initialize a queue with all interior edges
    illegal_edges = Queue()
    for edge in triangulation.interior_edges:
        if IsIllegal(edge, triangulation):
            illegal_edges.push(edge)
            
    # 2. Iteratively flip
    while not illegal_edges.empty():
        edge = illegal_edges.pop()
        
        # Re-check if it's still illegal (it might have been flipped already)
        if IsIllegal(edge, triangulation):
            # Perform the flip
            new_edge = Flip(edge, triangulation)
            
            # 3. Add neighbors to the queue
            # The 4 surrounding edges may now have become illegal
            for neighbor in GetNeighboringEdges(new_edge):
                if neighbor.is_interior:
                    illegal_edges.push(neighbor)
                    
    return triangulation

function IsIllegal(edge(B,C), triangulation):
    # Get the two triangles sharing the edge
    T1 = triangulation.GetFace(edge)
    T2 = triangulation.GetOppositeFace(edge)
    
    A = T1.vertex_opposite(edge)
    D = T2.vertex_opposite(edge)
    
    # Check if D is inside circumcircle of ABC
    return InCircle(A, B, C, D)
```

## 5. Parameters Selections
*   **Robust Predicates**: The `InCircle` test must be implemented using robust geometric predicates (e.g., using `orient2d` and `incircle` from Shewchuk) to handle floating-point precision issues.
*   **Data Structure**: A **Half-Edge** or **Quad-Edge** data structure is essential for efficiently finding neighboring faces and edges.

## 6. Complexity
*   **Time Complexity**: In the worst case, $O(n^2)$ flips may be required for $n$ points. However, starting from a "good" initial triangulation (like one from a sweep-line), it is often much faster.
*   **Space Complexity**: $O(n)$ to store the triangulation and the queue of edges.

## 7. Usages
*   **Mesh Refinement**: Improving the quality of an existing mesh for Finite Element analysis.
*   **Incremental Construction**: Maintaining a Delaunay triangulation as points are added or moved.
*   **Terrain Modeling**: Converting a set of elevation samples into a high-quality TIN (Triangulated Irregular Network).
*   **Fluid Simulation**: Re-meshing to avoid thin, sliver triangles that cause numerical instability.

## 8. Testing methods and Edge cases
*   **Co-circular Points**: Four points on a circle mean both diagonals are "legal." The algorithm should terminate consistently.
*   **Non-Convex Quadrilateral**: Ensure the flip logic only applies to convex quadrilaterals (though an illegal edge is guaranteed to be a diagonal of a convex quad).
*   **Boundary Edges**: Edges on the convex hull cannot be flipped.
*   **Sliver Triangles**: Verify that flips successfully remove extremely thin triangles.
*   **Convergence**: Test on highly structured point sets (like a grid) to ensure the algorithm doesn't loop infinitely due to precision errors.

## 9. References
*   Lawson, C. L. (1977). "Software for $C^1$ surface interpolation". Mathematical Software.
*   Guibas, L., & Stolfi, J. (1985). "Primitives for the manipulation of general subdivisions and the computation of Voronoi diagrams". ACM Transactions on Graphics.
*   Shewchuk, J. R. (1997). "Adaptive Precision Floating-Point Arithmetic and Fast Robust Geometric Predicates". Discrete & Computational Geometry.
*   Wikipedia: [Delaunay triangulation](https://en.wikipedia.org/wiki/Delaunay_triangulation)
