# Medial Axis Transform

## 1. Overview
The Medial Axis of a shape is the set of all points within the shape that have more than one closest point on the shape's boundary. Informally, it can be thought of as the "skeleton" or "midline" of the shape. Originally proposed by Harry Blum in 1967 as a tool for biological shape recognition, the Medial Axis Transform (MAT) is now a cornerstone of shape analysis, computer vision, and geometric modeling.

## 2. Definitions
*   **Medial Axis**: The locus of the centers of all maximal inscribed circles that touch the boundary in at least two points.
*   **Maximal Inscribed Circle**: A circle that is entirely contained within the shape and is not contained in any other such circle.
*   **Medial Axis Transform (MAT)**: The Medial Axis combined with the radius function (the radius of the maximal inscribed circle at each point).
*   **Bifurcation Point**: A point on the medial axis where the skeleton branches into multiple directions.

## 3. Theory
The Medial Axis can be understood through the **grassfire analogy**: if the boundary of a shape (represented by dry grass) is set on fire simultaneously at all points, the fire will propagate inward at a constant speed. The points where the fire fronts from different parts of the boundary meet and extinguish each other form the medial axis.

Mathematically, the medial axis of a polygon is composed of segments of **straight lines** (bisectors of two edges) and **parabolic arcs** (bisectors of an edge and a vertex). For 2D shapes, the medial axis is a 1D graph structure that topologically summarizes the 2D region.

## 4. Pseudo code
```python
function MedialAxis(polygon):
    # 1. Compute the Voronoi Diagram of the edges and vertices
    VD = Voronoi(polygon.edges, polygon.vertices)
    
    # 2. Filter the Voronoi edges
    skeleton_edges = []
    for edge in VD.edges:
        # Keep only edges that lie ENTIRELY inside the polygon
        if IsInside(edge, polygon):
            skeleton_edges.append(edge)
            
    # 3. Prune the skeleton
    # Remove "noise" branches caused by small boundary perturbations
    pruned_skeleton = Prune(skeleton_edges, threshold)
    
    return pruned_skeleton

function IsInside(edge, polygon):
    # Check if the midpoint of the Voronoi edge is inside the polygon
    return PointInPolygon(edge.midpoint, polygon)
```

## 5. Parameters Selections
*   **Pruning Threshold**: A crucial parameter that determines which branches are kept. Without pruning, even a tiny bump on the boundary creates a long branch in the medial axis.
*   **Voronoi Precision**: Robustness is key, especially when dealing with nearly collinear segments or sharp corners.

## 6. Complexity
*   **Time Complexity**: $O(n \log n)$ for a polygon with $n$ vertices, leveraging the fact that the medial axis is a subset of the Voronoi diagram of the polygon's edges and vertices.
*   **Space Complexity**: $O(n)$ to store the resulting graph structure.

## 7. Usages
*   **Character Recognition (OCR)**: Extracting the "bone" structure of letters for identification.
*   **Shape Simplification**: Representing complex 2D shapes by their 1D skeletons for faster processing.
*   **Motion Planning**: Finding the safest path for a robot (the medial axis is as far away from the walls as possible).
*   **Mesh Generation**: Using the skeleton to guide the placement of elements in a structured grid.
*   **Animation**: Creating skeletal rigs for 2D character deformation.

## 8. Testing methods and Edge cases
*   **Convex Polygons**: The medial axis is purely composed of straight line segments.
*   **Concave Polygons**: Contains parabolic segments where a vertex is the closest point to one side.
*   **Noise on Boundary**: Verify that pruning correctly handles small irregularities without destroying the main structure.
*   **Circular Shapes**: The medial axis of a perfect circle is a single point at its center.
*   **Parallel Edges**: The medial axis is exactly halfway between the edges.

## 9. References
*   Blum, H. (1967). "A Transformation for Extracting New Descriptors of Shape". Models for the Perception of Speech and Visual Form.
*   Chin, F., Snoeyink, J., & Wang, C. A. (1999). "Finding the Medial Axis of a Simple Polygon in Linear Time". Discrete & Computational Geometry.
*   Wikipedia: [Medial axis](https://en.wikipedia.org/wiki/Medial_axis)
