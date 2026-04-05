# Minimum Bounding Boxes

## 1. Overview
A minimum bounding box (MBB) is the smallest rectangle (in terms of area or perimeter) that contains all the points in a given set $P$. Unlike the axis-aligned bounding box (AABB), which is restricted to the coordinate axes, the minimum bounding box can be rotated to find the optimal fit. This problem is fundamental in object recognition, shape analysis, and spatial data compression.

## 2. Definitions
*   **AABB**: Axis-aligned bounding box (min/max $x$ and $y$ ).
*   **MBB**: Minimum area/perimeter bounding box (unconstrained orientation).
*   **Convex Hull**: The smallest convex set containing all points. The edges of the MBB are guaranteed to be collinear with at least one edge of the convex hull.
*   **Rotating Calipers**: An efficient technique for finding the MBB by "rotating" a set of four lines around the convex hull.

## 3. Theory
The minimum bounding box of a point set $P$ is identical to the MBB of its convex hull $CH(P)$. Freeman and Shapira (1975) proved that one edge of the minimum-area bounding box MUST be collinear with an edge of the convex hull.

The **Rotating Calipers** algorithm uses this property:
1.  Compute the convex hull $CH(P)$.
2.  Place four "calipers" (lines) touching the convex hull at its extreme points ($x_{min}, x_{max}, y_{min}, y_{max}$).
3.  Rotate the four lines simultaneously around the hull.
4.  Each time a line becomes collinear with an edge of the hull, calculate the area of the rectangle formed by the four lines.
5.  After a $90^\circ$ rotation, the minimum area found is the MBB.

## 4. Pseudo code
```python
function MinimumBoundingBox(points):
    # 1. Compute Convex Hull
    CH = ConvexHull(points)
    
    min_area = infinity
    best_rectangle = None
    
    # 2. Iterate through each edge of the hull
    for i in range(len(CH)):
        # Use edge (i, i+1) as the base orientation
        edge = CH[i+1] - CH[i]
        angle = atan2(edge.y, edge.x)
        
        # 3. Rotate hull so edge is horizontal
        rotated_hull = Rotate(CH, -angle)
        
        # 4. Find the min/max in the rotated frame
        min_x, max_x, min_y, max_y = GetBounds(rotated_hull)
        
        # 5. Calculate area
        area = (max_x - min_x) * (max_y - min_y)
        if area < min_area:
            min_area = area
            # 6. Store the rectangle (must rotate back to original frame)
            best_rectangle = RotateBack(Rectangle(min_x, max_x, min_y, max_y), angle)
            
    return best_rectangle
```

## 5. Parameters Selections
*   **Objective Function**: Usually **Area** is minimized, but **Perimeter** can also be an objective.
*   **Convex Hull Algorithm**: Graham Scan or Monotone Chain are suitable.

## 6. Complexity
*   **Time Complexity**: $O(n \log n)$ to build the convex hull, and $O(n)$ for the rotating calipers scan.
*   **Space Complexity**: $O(n)$ to store the convex hull.

## 7. Usages
*   **Object Recognition**: Normalizing the orientation of an object before comparing it to a database.
*   **Packaging and Bin Packing**: Finding the most space-efficient way to fit an object into a shipping container.
*   **Spatial Indexing**: Using tighter-fitting MBBs instead of AABBs in R-trees to reduce overlap and improve search performance.
*   **Computer Vision**: Finding the orientation of a rectangular object (e.g., a credit card or a license plate).
*   **Geographic Information Systems (GIS)**: Describing the extent of spatial features.

## 8. Testing methods and Edge cases
*   **Points forming a Circle**: The MBB should be a square.
*   **Already Axis-Aligned Rectangle**: The MBB should match the AABB.
*   **Points on a Line**: The MBB will have zero area.
*   **Rotated Rectangle**: Ensure the algorithm finds the correct orientation and area.
*   **Precision**: Use robust arithmetic for cross-products and distance calculations.

## 9. References
*   Freeman, H., & Shapira, R. (1975). "Determining the minimum-area encasing rectangle for an arbitrary closed curve". Communications of the ACM.
*   Toussaint, G. T. (1983). "Solving geometric problems with the rotating calipers". Proceedings of MELECON '83.
*   Wikipedia: [Minimum bounding box](https://en.wikipedia.org/wiki/Minimum_bounding_box)
