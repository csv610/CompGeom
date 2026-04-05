# Maximum Overlap

## 1. Overview
The maximum overlap problem asks for a point (or region) in space that is covered by the maximum number of geometric objects from a given set. For example, given a set of 1D intervals, finding the time when the most tasks are active simultaneously. In 2D, this often involves finding the location covered by the most rectangles or disks. It is a fundamental problem in scheduling, resource allocation, and signal processing.

## 2. Definitions
*   **Depth of a Point**: The number of objects that contain the point.
*   **Maximum Depth ($k$ )**: The maximum possible depth across all points in the domain.
*   **Intersection Graph**: A graph where nodes are objects and edges represent overlaps. Maximum overlap is related to the maximum clique problem in this graph.

## 3. Theory
### 1D Case (Intervals)
For $n$ intervals $[s_i, e_i]$, the maximum overlap can be found using a **sweep-line** approach:
1.  Treat all start and end points as "events."
2.  Sort events by coordinate.
3.  Traverse events: increment a counter for every start point and decrement for every end point.
4.  The maximum value reached by the counter is the maximum overlap.

### 2D Case (Rectangles)
For axis-aligned rectangles, the problem is solved by sweeping a vertical line across the plane:
1.  As the sweep line hits the left edge of a rectangle, the corresponding vertical interval is added to a **Segment Tree**.
2.  As it hits the right edge, the interval is removed.
3.  The Segment Tree maintains the maximum "coverage" count across its entire range efficiently.

## 4. Pseudo code
### 1D Interval Overlap
```python
function MaximumOverlap1D(intervals):
    events = []
    for s, e in intervals:
        events.append((s, +1)) # Start
        events.append((e, -1)) # End
        
    # Sort events by position
    # For equal positions, process +1 before -1 for inclusive intervals
    events.sort(key=lambda x: (x[0], -x[1]))
    
    max_count = 0
    current_count = 0
    best_pos = None
    
    for pos, type in events:
        current_count += type
        if current_count > max_count:
            max_count = current_count
            best_pos = pos
            
    return max_count, best_pos
```

## 5. Parameters Selections
*   **Boundary Inclusion**: Decide if intervals are open $(a, b)$ or closed $[a, b]$. This affects how events at the same coordinate are handled during the sort.
*   **Data Structure**: For 2D, a Segment Tree with lazy propagation is required to achieve $O(n \log n)$ time.

## 6. Complexity
*   **1D Complexity**: $O(n \log n)$ due to sorting the $2n$ endpoints.
*   **2D Complexity**: $O(n \log n)$ using a sweep-line and a Segment Tree.
*   **Space Complexity**: $O(n)$ to store the events and the tree structure.

## 7. Usages
*   **Scheduling**: Finding the peak number of concurrent users or tasks.
*   **Genomics**: Identifying "hotspots" where many DNA reads map to the same genomic location.
*   **VLSI Design**: Finding regions with the highest density of circuit components to prevent overheating.
*   **Finance**: Detecting when the most stock market orders are active in a specific price range.
*   **Sensor Networks**: Identifying regions covered by the most sensors (redundancy analysis).

## 8. Testing methods and Edge cases
*   **Disjoint Intervals**: Maximum overlap should be 1.
*   **Identical Intervals**: Maximum overlap should be $n$.
*   **Nested Intervals**: Ensure the algorithm handles intervals fully contained within each other.
*   **Zero-Length Intervals**: Points treated as intervals.
*   **Large Coordinates**: Precision check for very distant intervals.
*   **Touching Boundaries**: Verify behavior when intervals touch at a single point (overlap of 1 or 2 depending on inclusion rule).

## 9. References
*   Bentley, J. L., & Wood, D. (1980). "Algorithms for spectral and overlapping rectangles". SIAM Journal on Computing.
*   Cormen, T. H., Leiserson, C. E., Rivest, R. L., & Stein, C. (2009). "Introduction to Algorithms". MIT Press.
*   Wikipedia: [Interval tree](https://en.wikipedia.org/wiki/Interval_tree#Overlap_search_query)
