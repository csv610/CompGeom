# Segment Trees

## 1. Overview
A segment tree is a versatile tree data structure used for storing information about intervals or segments. It is primarily used for range queries where we need to find the sum, minimum, or maximum of a specified range of values in an array that can be updated. In computational geometry, segment trees are used to solve problems involving orthogonal segments and rectangles.

## 2. Definitions
*   **Segment Tree**: A binary tree where each node represents an interval of an array.
*   **Leaf Node**: Represents a single element of the array.
*   **Internal Node**: Represents the union of the intervals of its children.
*   **Lazy Propagation**: A technique to optimize range updates by delaying them until necessary.

## 3. Theory
A segment tree for an array of $n$ elements is built by recursively splitting the array in half. The root node represents the interval $[0, n-1]$. Each internal node representing $[L, R]$ has children representing $[L, mid]$ and $[mid+1, R]$.

To solve a **Range Sum Query** for $[qL, qR]$:
1.  If the current node's interval is fully within $[qL, qR]$, return the node's sum.
2.  If the current node's interval is completely outside $[qL, qR]$, return 0.
3.  Otherwise, recurse to both children and return the sum of their results.

For **Range Updates**, a naive approach would update all relevant leaves, taking $O(n)$ time. **Lazy Propagation** stores the update at the highest relevant internal node and pushes it down only when those children are accessed, maintaining $O(\log n)$ performance.

## 4. Pseudo code
```python
function Build(arr, node, start, end):
    if start == end:
        tree[node] = arr[start]
        return
        
    mid = (start + end) // 2
    Build(arr, 2*node, start, mid)
    Build(arr, 2*node+1, mid+1, end)
    tree[node] = tree[2*node] + tree[2*node+1]

function RangeQuery(node, start, end, qL, qR):
    if qR < start or end < qL:
        return 0 # Completely outside
        
    if qL <= start and end <= qR:
        return tree[node] # Completely inside
        
    mid = (start + end) // 2
    p1 = RangeQuery(2*node, start, mid, qL, qR)
    p2 = RangeQuery(2*node+1, mid+1, end, qL, qR)
    return p1 + p2
```

## 5. Parameters Selections
*   **Operator Choice**: The tree can store Sum, Min, Max, GCD, or any associative operator.
*   **Tree Size**: For an array of $n$ elements, the segment tree requires $4n$ space in an array-based implementation.

## 6. Complexity
*   **Build**: $O(n)$ to build from an array of $n$ elements.
*   **Query**: $O(\log n)$ for any range query.
*   **Update**: $O(\log n)$ for point or range updates (with lazy propagation).
*   **Space**: $O(n)$ to store the tree nodes.

## 7. Usages
*   **Range Minimum Query (RMQ)**: Finding the smallest value in a subarray.
*   **Computational Geometry (Bentley-Ottmann)**: Used as the status structure for identifying intersections between vertical segments during a horizontal sweep.
*   **Rectangle Union**: Calculating the area of the union of several rectangles (Klee's measure problem).
*   **Dynamic Connectivity**: Keeping track of connectivity in a graph that is undergoing edge insertions and deletions.
*   **Statistics**: Calculating running averages or variances in real-time data streams.

## 8. Testing methods and Edge cases
*   **Single Element Ranges**: Querying and updating a range where $qL == qR$.
*   **Full Array Query**: Querying the entire range $[0, n-1]$ should return the root node's value.
*   **Overlapping Updates**: Multiple range updates on overlapping segments should be correctly accumulated by lazy propagation.
*   **Power of Two vs. Arbitrary $n$**: Ensure the tree correctly handles array sizes that are not powers of two.
*   **Negative Values**: If using Min/Max, ensure negative numbers are handled correctly (e.g., initial values should be $-\infty$ or $+\infty$).

## 9. References
*   Bentley, J. L. (1977). "Algorithms for Klee's measure problem". Technical Report.
*   Cormen, T. H., Leiserson, C. E., Rivest, R. L., & Stein, C. (2009). "Introduction to Algorithms". MIT Press.
*   Wikipedia: [Segment tree](https://en.wikipedia.org/wiki/Segment_tree)
