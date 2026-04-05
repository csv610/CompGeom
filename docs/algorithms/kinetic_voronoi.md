# Kinetic Voronoi Diagrams

## 1. Overview
A kinetic Voronoi diagram is a data structure that maintains the Voronoi diagram of a set of moving points (sites). Unlike a static Voronoi diagram, where points are fixed, in a kinetic setting, the points move according to known trajectories (e.g., linear or algebraic functions of time). The goal is to update the topological structure of the diagram only at discrete time instances where the Voronoi property is violated.

## 2. Definitions
*   **Kinetic Data Structure (KDS)**: A framework for maintaining a geometric property of moving objects.
*   **Certificate**: A boolean predicate that guarantees the current topological structure is valid.
*   **Event**: A point in time when a certificate fails (becomes zero).
*   **Certificate Failure**: When four points become co-circular, a topological change (an edge flip in the dual Delaunay triangulation) is required.

## 3. Theory
The maintenance of a kinetic Voronoi diagram is performed through its dual, the **Kinetic Delaunay Triangulation**.
1.  **Certificates**: For every edge $(A, B)$ shared by triangles $ABC$ and $ABD$ in the Delaunay triangulation, a certificate is defined based on the **In-Circle** test: $InCircle(A(t), B(t), C(t), D(t)) \ge 0$.
2.  **Event Prediction**: The roots of the certificate function (which is typically a polynomial in $t$) are calculated to find the next time $t_{event}$ when the certificate will fail.
3.  **Event Queue**: All predicted event times are stored in a priority queue.
4.  **Topological Update**: When the current time reaches $t_{event}$, an **Edge Flip** is performed on the corresponding edge, and new certificates are generated for the affected triangles.

This approach is extremely efficient because the number of topological changes is usually much smaller than the number of time steps required for a naive sampling approach.

## 4. Pseudo code
```python
function MaintainKineticVoronoi(points, trajectories):
    # 1. Initialize static Delaunay Triangulation
    DT = DelaunayTriangulation(points)
    
    # 2. Predict events for all interior edges
    event_queue = PriorityQueue()
    for edge in DT.edges:
        t_fail = PredictFailureTime(edge, trajectories)
        if t_fail > current_time:
            event_queue.push(Event(t_fail, edge))
            
    # 3. Main simulation loop
    while current_time < end_time:
        event = event_queue.pop()
        current_time = event.time
        
        # 4. Handle topological change
        edge = event.edge
        new_edge = Flip(edge, DT)
        
        # 5. Update certificates for the 4 surrounding edges
        for neighbor in GetAffectedEdges(new_edge):
            UpdateEvent(neighbor, event_queue, trajectories)
```

## 5. Parameters Selections
*   **Trajectory Model**: Linear ($P(t) = P_0 + vt$) is common, but high-order algebraic paths can be handled using polynomial root solvers.
*   **Root Finding**: Efficient and robust numerical solvers are needed to find the *first* real root $t > t_{now}$ of the InCircle polynomial.

## 6. Complexity
*   **Event Count**: In the worst case, $O(n^2)$ topological changes for linear trajectories. In practice, it is often close to $O(n)$.
*   **Processing Time**: $O(\log n)$ per event to update the priority queue and perform the flip.

## 7. Usages
*   **Robotics**: Real-time path planning among moving obstacles.
*   **Crowd Simulation**: Modeling the personal space of individuals in a moving crowd.
*   **Air Traffic Control**: Tracking the "empty" space between moving aircraft.
*   **Bioinformatics**: Simulating the movement of atoms in a protein or cells in a tissue.
*   **Astronomy**: Tracking the evolution of cosmic structures over time.

## 8. Testing methods and Edge cases
*   **Zero Velocity**: Verify that the kinetic structure remains static and produces the same result as the static algorithm.
*   **Collisions**: Handle cases where two points occupy the same position (distance 0).
*   **Degenerate Co-circularity**: Multiple events occurring at the exact same time (e.g., points on a square lattice moving synchronously).
*   **Infinite Time**: Verify that the algorithm handles events predicted far in the future or that never occur.
*   **Boundary points**: Handle points moving out of the region of interest.

## 9. References
*   Basch, J., Guibas, L. J., & Hershberger, J. (1999). "Data structures for mobile data". Journal of Algorithms.
*   Guibas, L. J. (1998). "Kinetic data structures: A new recipe for dynamic geometric algorithms". ACM SIGART Bulletin.
*   Albers, G., Guibas, L. J., Mitchell, J. S., & Roos, T. (1998). "Voronoi diagrams of moving points". International Journal of Computational Geometry & Applications.
*   Wikipedia: [Kinetic data structure](https://en.wikipedia.org/wiki/Kinetic_data_structure)
