# Proximity Queries

## 1. Overview
Proximity queries are a class of geometric problems focused on finding the spatial relationships between objects, specifically their distances and relative positions. These queries answer questions like "Which object is closest to this point?", "Are these two objects intersecting?", or "How far apart are these two shapes?". Proximity queries are the foundation of collision detection, spatial data mining, and robotics.

## 2. Definitions
*   **Nearest Neighbor (NN)**: Finding the point in a set $P$ closest to a query point $Q$.
*   **K-Nearest Neighbors (k-NN)**: Finding the $k$ closest points.
*   **Closest Pair**: Finding the two points in a set $P$ with the minimum distance.
*   **Collision Detection (Intersection Query)**: Determining if two objects $A$ and $B$ share any common points.
*   **Distance Query**: Calculating the minimum Euclidean distance between two complex objects.

## 3. Theory
Proximity queries are categorized by the type of geometric objects involved:
1.  **Point-Point**: Handled using **KD-Trees** or **Quadtrees** for efficient $O(\log n)$ retrieval.
2.  **Point-Mesh**: Finding the closest point on a surface. This involves searching a spatial index (like an **AABB Tree** or **BVH**) and calculating the distance to each triangle in the candidate leaves.
3.  **Mesh-Mesh**: Calculating the distance between two 3D models. The **GJK (Gilbert-Johnson-Keerthi)** algorithm is the standard for convex shapes, while BVH hierarchies are used for general non-convex meshes.
4.  **All-Pairs**: Finding all pairs of objects within a distance $r$. This is solved using **Spatial Hashing** or sweep-line algorithms.

The efficiency of these queries relies heavily on **Spatial Partitioning** (dividing the space) or **Bounding Volume Hierarchies** (grouping the objects).

## 4. Pseudo code
### General Bounding Volume Hierarchy (BVH) Distance Query
```python
function Distance(nodeA, nodeB, current_min):
    # 1. Pruning: if the boxes are already further than current_min, stop
    if BoxDistance(nodeA.bbox, nodeB.bbox) >= current_min:
        return current_min
        
    # 2. Leaf Case: Calculate exact distance between primitives
    if nodeA.is_leaf and nodeB.is_leaf:
        for primA in nodeA.primitives:
            for primB in nodeB.primitives:
                d = PrimitiveDistance(primA, primB)
                current_min = min(current_min, d)
        return current_min
        
    # 3. Recursive Step: Split the larger node
    if nodeA.volume > nodeB.volume:
        for childA in nodeA.children:
            current_min = Distance(childA, nodeB, current_min)
    else:
        for childB in nodeB.children:
            current_min = Distance(nodeA, childB, current_min)
            
    return current_min
```

## 5. Parameters Selections
*   **Bounding Volume Type**: **AABB** (fast intersection), **OOBB** (tighter fit), or **Bounding Spheres** (rotation invariant).
*   **Spatial Index**: Use **KD-Trees** for static points and **R-Trees** or **BVHs** for moving objects.

## 6. Complexity
*   **Point NN**: $O(\log n)$ average using KD-Trees.
*   **Closest Pair**: $O(n \log n)$ deterministic or $O(n)$ randomized.
*   **Collision Detection**: $O(n \log n)$ for broad-phase, $O(1)$ for narrow-phase (convex primitives).

## 7. Usages
*   **Physics Engines**: Real-time collision detection in video games (e.g., PhysX, Bullet).
*   **Machine Learning**: Clustering (K-Means) and classification (KNN).
*   **Robotics**: Obstacle avoidance and sensor fusion.
*   **Molecular Modeling**: Detecting van der Waals overlaps between atoms.
*   **GIS**: Finding the nearest points of interest (e.g., hospitals or fire stations).

## 8. Testing methods and Edge cases
*   **Identical Objects**: Distance should be zero.
*   **Touching Objects**: Distance should be zero or very small.
*   **Nested Objects**: Ensure the algorithm detects if one object is entirely inside another.
*   **Large Aspect Ratios**: Test with very long and thin objects which can "leak" through poorly fitted bounding volumes.
*   **Precision**: Verify distances for objects separated by many orders of magnitude.

## 9. References
*   Gilbert, E. G., Johnson, D. W., & Keerthi, S. S. (1988). "A fast procedure for computing the distance between complex objects in three-dimensional space". IEEE Journal on Robotics and Automation.
*   Ericson, C. (2004). "Real-Time Collision Detection". Morgan Kaufmann.
*   Samet, H. (2006). "Foundations of Multidimensional and Metric Data Structures". Elsevier.
*   Wikipedia: [Nearest neighbor search](https://en.wikipedia.org/wiki/Nearest_neighbor_search)
