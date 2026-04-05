# Segment Intersection (Bentley-Ottmann)

## 1. Overview
The segment intersection problem asks for all intersection points among a set of $n$ line segments in the 2D plane. While a brute-force approach checks every pair of segments in $O(n^2)$ time, the Bentley-Ottmann algorithm uses a **sweep-line paradigm** to achieve a complexity that is sensitive to the number of intersections $k$. It is a cornerstone algorithm in computational geometry for applications in CAD, GIS, and computer graphics.

## 2. Definitions
*   **Sweep Line**: An imaginary vertical line that moves from left to right across the plane.
*   **Event Queue**: A priority queue containing points where the sweep line's status changes (endpoints of segments and intersection points).
*   **Sweep-Line Status**: A data structure (typically a balanced BST) that maintains the vertical order of segments currently intersecting the sweep line.
*   **Output-Sensitive**: An algorithm whose running time depends on the size of the input AND the size of the output.

## 3. Theory
The Bentley-Ottmann algorithm is based on the observation that two segments can only intersect if they are **adjacent** in the vertical order at some position along the sweep line.
1.  Initialize the event queue with all segment endpoints.
2.  Pop the next event point $P$.
3.  **If $P$ is a left endpoint**: Insert the segment into the status structure. Check for intersections with its immediate neighbors (above and below).
4.  **If $P$ is a right endpoint**: Check if its neighbors (above and below) now intersect each other. Remove the segment from the status structure.
5.  **If $P$ is an intersection point**: Report the intersection. Swap the order of the two intersecting segments in the status structure. Check for new intersections with their new neighbors.

This process ensures that all $k$ intersections are found by only checking pairs of segments that are "geographically" close.

## 4. Pseudo code
```python
function BentleyOttmann(segments):
    # 1. Initialize Event Queue with all endpoints
    events = PriorityQueue()
    for s in segments:
        events.push(Event(s.left, LEFT_ENDPOINT, s))
        events.push(Event(s.right, RIGHT_ENDPOINT, s))
        
    # 2. Sweep Line Status (Balanced BST)
    status = BalancedBST()
    intersections = []
    
    while not events.empty():
        event = events.pop()
        p = event.point
        
        if event.type == LEFT_ENDPOINT:
            s = event.segment
            status.insert(s, p.x)
            above, below = status.neighbors(s)
            CheckIntersection(s, above, events)
            CheckIntersection(s, below, events)
            
        elif event.type == RIGHT_ENDPOINT:
            s = event.segment
            above, below = status.neighbors(s)
            status.remove(s)
            CheckIntersection(above, below, events)
            
        elif event.type == INTERSECTION:
            s1, s2 = event.segments
            intersections.append(p)
            # Swap order in BST
            status.swap(s1, s2)
            # Check new neighbors
            new_above = status.above(s2)
            new_below = status.below(s1)
            CheckIntersection(s2, new_above, events)
            CheckIntersection(s1, new_below, events)
            
    return intersections
```

## 5. Parameters Selections
*   **Precision**: Highly sensitive to floating-point errors. Use robust geometric predicates for intersection calculation and segment ordering.
*   **Degeneracies**: Multiple segments intersecting at the same point or vertical segments require careful handling.

## 6. Complexity
*   **Time Complexity**: $O((n + k) \log n)$, where $n$ is the number of segments and $k$ is the number of intersections.
*   **Space Complexity**: $O(n + k)$ to store the event queue and status structure.

## 7. Usages
*   **Map Overlay**: Combining two maps (e.g., roads and counties) to find where they cross.
*   **Boolean Operations**: Preprocessing for polygon union/intersection.
*   **CAD/CAM**: Detecting errors in mechanical drawings (e.g., overlapping paths).
*   **VLSI Design**: Checking for short circuits in circuit board traces.
*   **Path Planning**: Determining if a path intersects any obstacles.

## 8. Testing methods and Edge cases
*   **No Intersections**: The algorithm should only process $2n$ events and return empty.
*   **All segments intersect at one point**: Verify that the event queue handles multiple events at the same location.
*   **Vertical Segments**: Ensure the ordering logic correctly handles segments with the same $x$-coordinate.
*   **Collinear Segments**: Overlapping segments on the same line.
*   **Duplicate Intersections**: Ensure each intersection point is reported only once if multiple segments meet.

## 9. References
*   Bentley, J. L., & Ottmann, T. A. (1979). "Algorithms for reporting and counting geometric intersections". IEEE Transactions on Computers.
*   Berg, M. de, Cheong, O., Kreveld, M. van, & Overmars, M. (2008). "Computational Geometry: Algorithms and Applications". Springer-Verlag.
*   Wikipedia: [Bentley–Ottmann algorithm](https://en.wikipedia.org/wiki/Bentley%E2%80%93Ottmann_algorithm)
