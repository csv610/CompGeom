# Interval Trees

## 1. Overview
An interval tree is a balanced binary search tree used to store segments (intervals) and allow for efficient range queries. Specifically, it is designed to answer the question: "Which of the stored intervals overlap with a given query interval $[x, y]$?" Interval trees are an essential tool in computational geometry for solving 1D segment intersection problems and are a key component of more complex spatial structures.

## 2. Definitions
*   **Interval**: A pair of numbers $[start, end]$.
*   **Overlap**: Two intervals $[a, b]$ and $[c, d]$ overlap if $a \le d$ and $c \le b$.
*   **Node**: Each node in the tree stores a single interval and the maximum value $max$ found in its subtree.
*   **Max Value**: For any node $N$, $N.max = \max(N.interval.end, N.left.max, N.right.max)$.

## 3. Theory
The interval tree is built using the **start point** of each interval as the key in a standard binary search tree. Each node additionally maintains the maximum endpoint of all intervals in its subtree. This "max" property is key for efficient pruning during a query.

To search for an interval overlapping with $[q_{start}, q_{end}]$:
1.  Check if the current node's interval overlaps.
2.  If the left child exists and its $max$ is $\ge q_{start}$, we must search the left branch (there could be an overlap there).
3.  Otherwise, we only search the right branch.

This pruning logic ensures that we don't explore subtrees that cannot possibly contain an overlapping interval.

## 4. Pseudo code
```python
function Insert(node, interval):
    if node is None:
        return Node(interval, interval.end)
        
    if interval.start < node.interval.start:
        node.left = Insert(node.left, interval)
    else:
        node.right = Insert(node.right, interval)
        
    # Update the max endpoint in this subtree
    node.max = max(node.max, interval.end)
    return node

function FindOverlaps(node, query, results):
    if node is None:
        return
        
    # Check current node
    if Overlaps(node.interval, query):
        results.append(node.interval)
        
    # Choose branch
    if node.left is not None and node.left.max >= query.start:
        FindOverlaps(node.left, query, results)
        
    # Always check right if there's potentially an overlap
    # We can skip if node.interval.start > query.end
    if node.right is not None and node.right.max >= query.start:
        FindOverlaps(node.right, query, results)
```

## 5. Parameters Selections
*   **Balancing**: To maintain $O(\log n)$ performance, the underlying BST should be a self-balancing tree like an **AVL Tree** or a **Red-Black Tree**.
*   **Interval Type**: The tree can handle open, closed, or half-open intervals with consistent comparison logic.

## 6. Complexity
*   **Construction**: $O(n \log n)$ to insert $n$ intervals into a balanced tree.
*   **Query**: $O(k + \log n)$, where $k$ is the number of overlapping intervals found. In the worst case (searching for all overlaps), it takes $O(n)$.
*   **Space**: $O(n)$ to store each interval exactly once.

## 7. Usages
*   **Resource Allocation**: Finding all booked time slots that conflict with a new appointment.
*   **VLSI Design**: Design rule checking (checking for overlapping wires on a chip).
*   **Database Indexing**: Efficiently searching through time-series data or ranges.
*   **Ray Tracing**: 1D interval trees (often called "segment trees" in this context) are used to find all objects a ray passes through.
*   **Video Games**: Managing "life spans" or "event timelines."

## 8. Testing methods and Edge cases
*   **Contained Intervals**: An interval $[5, 10]$ fully containing another $[6, 7]$.
*   **Sharing Boundaries**: Intervals $[5, 10]$ and $[10, 15]$ overlapping only at 10.
*   **Large and Small Max values**: Ensure the `node.max` correctly propagates from the leaves to the root.
*   **Disconnected Intervals**: Searching for overlaps in a region with no intervals.
*   **Identical Intervals**: Multiple nodes with the exact same $[start, end]$.

## 9. References
*   Edelsbrunner, H. (1980). "Dynamic data structures for orthogonal intersection queries". Technical Report.
*   Cormen, T. H., Leiserson, C. E., Rivest, R. L., & Stein, C. (2009). "Introduction to Algorithms". MIT Press.
*   Wikipedia: [Interval tree](https://en.wikipedia.org/wiki/Interval_tree)
