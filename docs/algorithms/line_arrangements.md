# Line Arrangements

## 1. Overview
A line arrangement is the subdivision of the 2D plane induced by a set of $n$ lines. It is a fundamental structure in computational geometry that encodes all intersection points and the topological relationships between the lines (vertices, edges, and faces). Arrangements provide a geometric framework for solving problems involving duality, range searching, and visibility.

## 2. Definitions
*   **Arrangement ($\mathcal{A}(L)$)**: The subdivision of the plane into vertices (intersections), edges (segments between intersections), and faces (convex regions).
*   **Vertex**: The intersection point of two or more lines.
*   **Edge**: A maximal connected portion of a line that does not contain any vertices.
*   **Face**: A maximal connected portion of the plane that does not contain any points of any lines.
*   **Zone**: The set of faces in an arrangement that are intersected by a new line.

## 3. Theory
For $n$ lines in **general position** (no two lines parallel, no three lines concurrent):
*   Number of vertices: $\binom{n}{2} = \frac{n(n-1)}{2}$.
*   Number of edges: $n^2$.
*   Number of faces: $\frac{n^2 + n + 2}{2}$.

The standard way to build an arrangement is through **incremental construction**:
1.  Start with a simple arrangement of two lines.
2.  Add lines one by one. For each new line $l_i$:
    *   Find the face containing one end of $l_i$.
    *   Trace the path of $l_i$ through the arrangement using the **Zone Theorem**, which states that the complexity of the zone of a line is $O(n)$.
    *   Split edges and faces as $l_i$ passes through them.

## 4. Pseudo code
```python
function BuildArrangement(lines):
    # 1. Initialize with a large bounding box
    arrangement = InitializeDCEL() 
    
    # 2. Add lines incrementally
    for line in lines:
        # 3. Locate start face
        face = LocateFace(arrangement, line.start_point)
        
        # 4. Trace the line through the arrangement (Zone Walk)
        current_p = line.start_point
        while not IsFinished(current_p):
            # Find which edge of the current face the line exits through
            exit_edge = FindExitEdge(face, line)
            
            # Split the face and update the DCEL
            arrangement.SplitFace(face, line, exit_edge)
            
            # Move to the adjacent face
            face = arrangement.GetAdjacentFace(exit_edge)
            current_p = arrangement.GetIntersection(line, exit_edge)
            
    return arrangement
```

## 5. Parameters Selections
*   **Data Structure**: The **Doubly-Connected Edge List (DCEL)** is the standard choice for representing arrangements as it allows for efficient traversal of vertices, edges, and faces.
*   **General Position**: If lines can be parallel or concurrent, the construction algorithm must use robust handling for these degeneracies.

## 6. Complexity
*   **Time Complexity**: $O(n^2)$ using the incremental construction based on the Zone Theorem.
*   **Space Complexity**: $O(n^2)$ to store all vertices, edges, and faces.

## 7. Usages
*   **Duality Problems**: Many problems involving points can be solved by mapping them to lines in a dual plane and analyzing their arrangement (e.g., finding the maximum number of collinear points).
*   **Visibility**: Computing the visibility graph of a set of obstacles.
*   **Motion Planning**: Analyzing the complexity of the configuration space for a robot.
*   **Range Searching**: Identifying all points within a specific region.
*   **Statistical Analysis**: Finding the Theil-Sen estimator or other robust regression lines.

## 8. Testing methods and Edge cases
*   **Parallel Lines**: Verify that the algorithm correctly creates regions between lines that never intersect.
*   **Concurrent Lines**: Ensure that three or more lines meeting at a single point are handled without creating zero-length edges.
*   **Horizontal/Vertical Lines**: Test with lines aligned to the axes.
*   **Small $n$**: Verify the formula for $n=1, 2, 3$.
*   **Bounding Box**: Ensure the arrangement handles lines that extend to infinity correctly by using a sufficiently large bounding volume or symbolic coordinates.

## 9. References
*   Edelsbrunner, H., O'Rourke, J., & Seidel, R. (1986). "Constructing arrangements of lines and hyperplanes with applications". SIAM Journal on Computing.
*   Chazelle, B., Guibas, L. J., & Lee, D. T. (1985). "The power of geometric duality". BIT Numerical Mathematics.
*   Berg, M. de, Cheong, O., Kreveld, M. van, & Overmars, M. (2008). "Computational Geometry: Algorithms and Applications". Springer-Verlag.
*   Wikipedia: [Arrangement of lines](https://en.wikipedia.org/wiki/Arrangement_of_lines)
