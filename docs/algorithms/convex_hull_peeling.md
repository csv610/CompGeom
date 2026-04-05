# Convex Hull Peeling (Onion Peeling)

## 1. Overview
Convex hull peeling, also known as "onion peeling," is a recursive process of identifying and removing the convex hull of a point set. After the first hull is removed, the process is repeated on the remaining points until no points are left. This decomposition organizes a set of points into nested "layers," similar to the layers of an onion. It is a fundamental technique for robust statistics, data depth analysis, and identifying outliers.

## 2. Definitions
*   **Convex Hull Layer**: A set of points that form the boundary of the convex hull at a specific iteration.
*   **Convex Hull Depth (Layer Number)**: The iteration number in which a point is removed. Points on the outermost hull have depth 1.
*   **Median Point(s)**: The points remaining in the final, innermost layer.

## 3. Theory
The onion peeling of a point set $P$ provides a natural way to measure the "centrality" of points. 
1.  Compute the convex hull $CH(P)$.
2.  The points on the boundary of $CH(P)$ form the first layer $L_1$.
3.  Let $P' = P \setminus L_1$.
4.  Repeat the process on $P'$ to find $L_2, L_3, \dots, L_k$.

In 2D, the total number of layers $k$ is roughly $O(n^{2/3})$ for points distributed uniformly in a square. The structure of the layers can be used to define the **Tukey Depth** (or location depth) of points in a multivariate dataset.

## 4. Pseudo code
```python
function ConvexHullPeeling(points):
    layers = []
    current_points = set(points)
    
    while current_points:
        # 1. Compute hull of remaining points
        if len(current_points) < 3:
            layers.append(list(current_points))
            break
            
        hull_indices = ComputeConvexHull(list(current_points))
        hull_points = [list(current_points)[i] for i in hull_indices]
        
        # 2. Store the current layer
        layers.append(hull_points)
        
        # 3. Peel the layer
        for p in hull_points:
            current_points.remove(p)
            
    return layers
```

## 5. Parameters Selections
*   **Hull Algorithm**: Monotone Chain or Graham Scan are ideal for 2D. For 3D, QuickHull is standard.
*   **Handling Collinearity**: Points that lie exactly on the edges of the convex hull can either be included in the current layer or treated as interior points for the next layer. Including them is more common in statistics.

## 6. Complexity
*   **Naive Complexity**: $O(n^2)$ if a new $O(n \log n)$ hull is calculated for every point removed.
*   **Efficient 2D Complexity**: $O(n \log n)$ using Chazelle's algorithm, which uses a more complex data structure to update the hull as points are removed.
*   **Space Complexity**: $O(n)$ to store the point set and the layer indices.

## 7. Usages
*   **Robust Statistics**: Identifying the "geometric median" of a point set by finding the deepest onion layer.
*   **Outlier Detection**: Points in the first few layers are candidates for being outliers or "extreme" values.
*   **Data Visualization**: Creating "bagplots" or "boxplots" for 2D data.
*   **Pattern Recognition**: Describing the density and distribution of a point cloud.
*   **Computational Geometry**: A preprocessing step for certain range-searching and visibility problems.

## 8. Testing methods and Edge cases
*   **Perfectly Collinear Points**: All points should be removed in the first layer.
*   **Points on a Circle**: All points should be removed in the first layer.
*   **Grid Arrangement**: Verify that the peeling correctly identifies the nested squares or rectangles.
*   **Small Sets**: Test with $n=1, 2, 3$.
*   **Symmetry**: For a symmetric distribution, the layers should maintain that symmetry.

## 9. References
*   Chazelle, B. (1985). "On the convex layers of a planar set". IEEE Transactions on Information Theory.
*   Overmars, M. H., & Leeuwen, J. van. (1981). "Maintenance of configurations in the plane". Journal of Computer and System Sciences.
*   Tukey, J. W. (1975). "Mathematics and the picturing of data". Proceedings of the International Congress of Mathematicians.
*   Wikipedia: [Convex layers](https://en.wikipedia.org/wiki/Convex_layers)
