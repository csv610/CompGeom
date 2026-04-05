# R-Trees (Rectangle Trees)

## 1. Overview
An R-tree is a tree data structure used for efficient spatial indexing of multidimensional information, particularly objects represented as Minimum Bounding Rectangles (MBRs). Unlike KD-trees or quadtrees, which partition the space itself, R-trees group the objects into hierarchical, potentially overlapping regions. This makes R-trees exceptionally well-suited for disk-based databases and large-scale spatial datasets.

## 2. Definitions
*   **Minimum Bounding Rectangle (MBR)**: The smallest rectangle that contains all the elements in a node's subtree.
*   **Leaf Node**: Stores pointers to the actual geometric objects and their MBRs.
*   **Internal Node**: Stores a pointer to a child node and the MBR of that child.
*   **Balance**: R-trees are always height-balanced, similar to B-trees.

## 3. Theory
R-trees are built by grouping nearby objects and enclosing them in their MBR.
1.  **Insertion**: To insert an object, we start at the root and recursively choose a child node whose MBR requires the least expansion to include the new object. 
2.  **Node Splitting**: When a node exceeds its capacity, it must be split into two. Since the choice of split affects search performance, heuristics are used to minimize the area and overlap of the two new MBRs (e.g., Quadratic Split or Linear Split).
3.  **Search**: To find objects in a query region, we traverse all branches whose MBRs intersect the query. Because MBRs at the same level can overlap, multiple branches may need to be explored.

## 4. Pseudo code
```python
function Search(node, query_rect):
    results = []
    if node.is_leaf:
        for obj in node.objects:
            if Intersects(obj.mbr, query_rect):
                results.append(obj)
    else:
        for child in node.children:
            if Intersects(child.mbr, query_rect):
                results.extend(Search(child, query_rect))
    return results

function Insert(node, obj):
    if node.is_leaf:
        node.add(obj)
        if node.count > MAX_CAPACITY:
            return Split(node) # Returns two nodes
    else:
        # 1. Choose subtree that requires least area expansion
        child = ChooseBestSubtree(node, obj)
        split_result = Insert(child, obj)
        
        # 2. Update node's MBR
        node.mbr = Union(node.mbr, obj.mbr)
        
        # 3. Handle split if it occurred in child
        if split_result is not None:
            node.add_child(split_result)
            if node.child_count > MAX_CAPACITY:
                return Split(node)
    return None
```

## 5. Parameters Selections
*   **Split Algorithm**: **Guttman's Quadratic Split** is common. The **R*-Tree** variant uses a more complex split heuristic that also considers overlap and perimeter, leading to significantly better search performance.
*   **Min/Max Capacity**: Typically, nodes are required to be at least 40% full to maintain balance and storage efficiency.

## 6. Complexity
*   **Insertion**: $O(\log_M n)$ where $M$ is the maximum node capacity. Worst case $O(n)$ if many splits occur.
*   **Search**: Average $O(\log_M n)$ for localized queries. Worst case $O(n)$ if the MBRs have excessive overlap.
*   **Space**: $O(n)$ to store each object and the hierarchy.

## 7. Usages
*   **Spatial Databases**: The core indexing mechanism for PostGIS, Oracle Spatial, and MySQL Spatial.
*   **GIS**: Indexing road networks, parcels, and satellite imagery.
*   **Network Analysis**: Routing and nearest-neighbor searches in complex maps.
*   **Computer Graphics**: Managing large scenes with many individual models.
*   **Internet of Things (IoT)**: Real-time tracking and querying of moving sensors or vehicles.

## 8. Testing methods and Edge cases
*   **Highly Overlapping Objects**: Ensure the tree doesn't degrade into a linked list when many objects occupy the same space.
*   **Large Objects**: A single large rectangle can intersect many MBRs, causing search to slow down.
*   **Empty Search**: Verify the algorithm correctly identifies when no objects are in the query area.
*   **Bulk Loading**: For static datasets, use a "Sort-Tile-Recursive" (STR) bulk loader to build a nearly optimal tree.
*   **Deletion**: R-trees handle deletions by merging nodes if they fall below minimum capacity.

## 9. References
*   Guttman, A. (1984). "R-trees: A dynamic index structure for spatial searching". SIGMOD.
*   Beckmann, N., Kriegel, H. P., Schneider, R., & Seeger, B. (1990). "The R*-tree: An efficient and robust access method for points and rectangles". SIGMOD.
*   Wikipedia: [R-tree](https://en.wikipedia.org/wiki/R-tree)
