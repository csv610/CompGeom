# Straight Skeleton

## 1. Overview
The straight skeleton of a polygon is a 1D skeleton structure topologically similar to the medial axis, but composed entirely of straight line segments. It is formed by a "wavefront propagation" process where the edges of the polygon move inward parallel to themselves at a constant speed. The paths traced by the vertices of the shrinking polygon form the straight skeleton.

## 2. Definitions
*   **Straight Skeleton**: The locus of vertices as the edges of a polygon move inward at a uniform speed.
*   **Wavefront**: The shrinking polygon boundary at any point in time during the propagation.
*   **Bisector**: The ray originating from a polygon vertex that bisects the angle formed by its two incident edges.
*   **Edge Event**: An edge shrinks to zero length and disappears, causing its two neighboring vertices to merge into one.
*   **Split Event**: A vertex moves into and splits an edge of the wavefront into two separate parts.

## 3. Theory
Unlike the medial axis, which can contain curved (parabolic) segments, the straight skeleton is piecewise linear because each point on the skeleton is the intersection of two straight-line edge trajectories.

The construction of a straight skeleton is typically modeled as a **kinetic process**. We keep track of the time until the next "event" (either an edge disappearing or an edge being split). As events occur, the topology of the wavefront changes, and new events are calculated. This process continues until the entire polygon has collapsed.

## 4. Pseudo code
```python
function StraightSkeleton(polygon):
    # 1. Initialize bisectors for all vertices
    events = PriorityQueue()
    for v in polygon.vertices:
        events.push(CalculateNextEvent(v, polygon))
        
    skeleton_edges = []
    
    # 2. Process events in order of time
    while not events.empty():
        event = events.pop()
        
        if event.type == "EDGE":
            HandleEdgeEvent(event, skeleton_edges, events)
        elif event.type == "SPLIT":
            HandleSplitEvent(event, skeleton_edges, events)
            
        # 3. Update neighboring events
        UpdateNeighbors(event, events)
        
    return skeleton_edges
```

## 5. Parameters Selections
*   **Precision**: Highly sensitive to numerical precision during event time calculations, especially for nearly parallel edges.
*   **Degeneracies**: Multiple events occurring at the exact same time (e.g., in a square or a regular hexagon) must be handled carefully.

## 6. Complexity
*   **Time Complexity**: $O(n \log n)$ for simple polygons, using more advanced data structures (like kinetic priority queues). A simpler $O(n^2)$ approach is often implemented.
*   **Space Complexity**: $O(n)$ to store the polygon wavefront and the resulting skeleton edges.

## 7. Usages
*   **Roof Construction**: Defining the ridges and valleys of a roof for a given house footprint.
*   **Corridor Generation**: Creating paths in architectural layouts.
*   **Offsetting**: Generating inward/outward offsets of polygons (mitered offsets).
*   **Computer Graphics**: Creating "puffy" 3D effects from 2D shapes (Beveling).
*   **GIS**: Generating centerlines of road networks.

## 8. Testing methods and Edge cases
*   **Convex Polygons**: In this case, the straight skeleton and the medial axis are topologically similar, though the straight skeleton remains linear.
*   **Concave Polygons**: Split events are common and must be handled to ensure the skeleton correctly reflects the topology.
*   **Holes**: The straight skeleton can be extended to polygons with holes, where the outer boundary moves in and the holes move out.
*   **Collinear Edges**: Edges that are almost in a straight line can lead to events far into the future (numerical instability).
*   **Symmetry**: Regular polygons should result in a perfectly symmetric skeleton meeting at a single point.

## 9. References
*   Aichholzer, O., Aurenhammer, F., Alberts, D., & Gärtner, B. (1995). "A novel type of skeleton for polygons". Journal of Universal Computer Science.
*   Eppstein, D., & Erickson, J. (1999). "Raising Roofs, Formulating Foundations, and Dissecting Designs: Techniques for Discrete Dirichlet Problems". Discrete & Computational Geometry.
*   Wikipedia: [Straight skeleton](https://en.wikipedia.org/wiki/Straight_skeleton)
