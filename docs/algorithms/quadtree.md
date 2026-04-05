# Quadtrees

## 1. Overview
A quadtree is a tree data structure in which each internal node has exactly four children. It is most commonly used to partition a two-dimensional space by recursively subdividing it into four quadrants (North-West, North-East, South-West, South-East). Quadtrees are the 2D equivalent of Octrees (used in 3D) and are essential for efficient spatial querying, image compression, and collision detection.

## 2. Definitions
*   **Root**: The top-level node representing the entire bounding area.
*   **Leaf**: A node that contains actual data points or a uniform value and has no children.
*   **Quadrant**: One of the four rectangular regions created by splitting a parent node's region in half along both the x and y axes.
*   **Capacity**: The maximum number of points a single node can hold before it must be split into four children.

## 3. Theory
A quadtree is built by starting with a bounding box and inserting points one by one. If a point is inserted into a leaf node that is already at its capacity, the node "subdivides" into four children, and all points in the node are redistributed to the correct child. 

For **Range Querying** (e.g., finding all points within a circle or rectangle), the quadtree allows us to quickly discard entire branches of the tree if their bounding box does not intersect the query area. This pruning results in $O(\log n)$ performance for localized searches.

## 4. Pseudo code
```python
function Insert(node, point):
    if not node.boundary.contains(point):
        return False
        
    if len(node.points) < node.capacity and not node.is_divided:
        node.points.append(point)
        return True
        
    if not node.is_divided:
        node.subdivide()
        
    # Try inserting into children
    if node.nw.insert(point): return True
    if node.ne.insert(point): return True
    if node.sw.insert(point): return True
    if node.se.insert(point): return True

function Query(node, range, result):
    if not node.boundary.intersects(range):
        return
        
    # Check points in current node
    for p in node.points:
        if range.contains(p):
            result.append(p)
            
    # Check children
    if node.is_divided:
        Query(node.nw, range, result)
        Query(node.ne, range, result)
        Query(node.sw, range, result)
        Query(node.se, range, result)
```

## 5. Parameters Selections
*   **Node Capacity**: Typically set to 4–16 points. Higher capacity reduces the number of nodes but increases the linear search time within each node.
*   **Maximum Depth**: A limit on subdivision to prevent infinite recursion in the case of overlapping or very dense points.

## 6. Complexity
*   **Construction**: $O(n \log n)$ in the average case. Worst case can be $O(n \cdot depth)$ if points are heavily clustered.
*   **Query**: $O(\log n)$ for average range queries.
*   **Space**: $O(n)$ in most cases, though the overhead of internal nodes can be significant if the tree is deep.

## 7. Usages
*   **Collision Detection**: Quickly finding pairs of objects that are close enough to collide.
*   **Image Compression**: Representing regions of uniform color with a single large node (e.g., in the TGA or PNG-like formats).
*   **Video Games**: View frustum culling (rendering only objects that are visible within the camera's FOV).
*   **GIS**: Storing and querying map features like road networks or city locations.
*   **Particle Systems**: Efficiently calculating local forces (e.g., gravity or repulsion) in many-body simulations.

## 8. Testing methods and Edge cases
*   **Uniform Point Distribution**: Verify that the tree divides evenly into a balanced structure.
*   **Points on Boundaries**: Ensure points exactly on the dividing lines are assigned to exactly one child.
*   **High-Density Clusters**: Ensure the "capacity" and "max depth" parameters prevent excessive subdivision.
*   **Empty Areas**: Verify that large regions with no points are represented by a single empty leaf node.
*   **Resizing**: Test if the quadtree can handle a dynamic bounding box or if it requires a fixed initial area.

## 9. References
*   Finkel, R. A., & Bentley, J. L. (1974). "Quad trees: A data structure for retrieval on composite keys". Acta Informatica.
*   Samet, H. (1984). "The Quadtree and Related Hierarchical Data Structures". ACM Computing Surveys.
*   Wikipedia: [Quadtree](https://en.wikipedia.org/wiki/Quadtree)
