# K-Dimensional Trees (KD-Trees)

## 1. Overview
A KD-tree is a space-partitioning data structure for organizing points in a $k$-dimensional space. It is a binary tree where every node is a $k$-dimensional point and every non-leaf node represents a splitting hyperplane. This structure is extremely efficient for range searches and nearest neighbor queries in low-to-medium dimensional spaces.

## 2. Definitions
*   **Splitting Hyperplane**: A $(k-1)$-dimensional surface that divides the point set into two subsets. It is always perpendicular to one of the coordinate axes.
*   **Depth (d)**: The level of a node in the tree. The splitting axis is typically chosen as `axis = d % k`.
*   **Median**: The point chosen to split the set at each node, ensuring the tree is balanced.
*   **Bounding Box**: The region of space represented by a specific node and all its descendants.

## 3. Theory
A KD-tree is built by recursively partitioning the set of points. At each level, the algorithm chooses one of the $k$ dimensions and splits the points into two groups: those whose coordinate in that dimension is less than the median and those whose coordinate is greater. 

For **Nearest Neighbor Search**, the tree is traversed from the root down to the leaf containing the query point. The distance from the query to this leaf is our initial "best" distance. Then, the algorithm backtracks up the tree, checking if any other branches could contain a closer point. This is done by checking if the query point's distance to a node's splitting hyperplane is smaller than the current best distance.

## 4. Pseudo code
```python
function BuildKDTree(points, depth=0):
    if not points: return None
    
    # 1. Choose splitting axis
    k = len(points[0])
    axis = depth % k
    
    # 2. Sort points by axis and find median
    points.sort(key=lambda x: x[axis])
    mid = len(points) // 2
    
    # 3. Create node and recurse
    node = Node(points[mid])
    node.left = BuildKDTree(points[:mid], depth + 1)
    node.right = BuildKDTree(points[mid+1:], depth + 1)
    
    return node

function NearestNeighbor(root, query, depth=0, best=None):
    if root is None: return best
    
    k = len(query)
    axis = depth % k
    
    # Update current best
    dist = EuclideanDistance(root.point, query)
    if best is None or dist < EuclideanDistance(best.point, query):
        best = root
        
    # Choose branch
    next_branch = root.left if query[axis] < root.point[axis] else root.right
    other_branch = root.right if query[axis] < root.point[axis] else root.left
    
    # Go down the chosen branch
    best = NearestNeighbor(next_branch, query, depth + 1, best)
    
    # Check if we need to explore the other branch
    if abs(query[axis] - root.point[axis]) < EuclideanDistance(best.point, query):
        best = NearestNeighbor(other_branch, query, depth + 1, best)
        
    return best
```

## 5. Parameters Selections
*   **Dimension Cycling**: Standard axis choice is `d % k`, but choosing the dimension with the largest variance (spread) can lead to more efficient searches.
*   **Leaf Size**: Storing a few points (e.g., 5–10) in each leaf instead of one can reduce recursion depth and improve performance.

## 6. Complexity
*   **Construction**: $O(n \log n)$ if sorting is done at each level, or $O(n \log n)$ with a pre-sorted approach or a linear-time median finding algorithm.
*   **Search**: $O(\log n)$ average time for nearest neighbor queries in low dimensions. In the worst case (e.g., high dimensions or skewed data), it can degrade to $O(n)$.
*   **Space**: $O(n)$ to store all points in the tree structure.

## 7. Usages
*   **Computational Geometry**: Fast point location and range searching.
*   **Machine Learning**: K-Nearest Neighbors (KNN) classification and clustering.
*   **Computer Graphics**: Ray tracing (finding the first object a ray intersects) and photon mapping.
*   **Data Compression**: Efficient representation of multidimensional datasets.
*   **GIS**: Finding the closest point of interest (e.g., "find the nearest gas station").

## 8. Testing methods and Edge cases
*   **Duplicate Points**: Ensure the tree correctly handles multiple points at the same coordinates.
*   **Points on Boundaries**: Correctly assign points that lie exactly on a splitting hyperplane.
*   **Empty Tree**: Handle $n=0$ cases gracefully.
*   **Very High Dimensions**: The "Curse of Dimensionality" affects KD-trees ($k > 20$); performance should be monitored.
*   **Skewed Data**: Test on points that are nearly collinear or form very narrow clusters.

## 9. References
*   Bentley, J. L. (1975). "Multidimensional binary search trees used for associative searching". Communications of the ACM.
*   Friedman, J. H., Bentley, J. L., & Finkel, R. A. (1977). "An Algorithm for Finding Best Matches in Logarithmic Expected Time". ACM Transactions on Mathematical Software.
*   Wikipedia: [k-d tree](https://en.wikipedia.org/wiki/K-d_tree)
