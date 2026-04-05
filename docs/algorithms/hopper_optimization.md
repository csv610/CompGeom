# Hopper Optimization (Non-Convex Packing)

## 1. Overview
Hopper optimization is a specialized technique for packing non-convex polygons into a rectangular container (the "hopper") such that the vertical height used is minimized. Unlike standard bin packing, which often uses bounding boxes, hopper optimization uses the exact geometry of the polygons, often leveraging the **No-Fit Polygon (NFP)** to find the tightest possible nesting. It is widely used in the textile, leather, and metal industries where material waste must be minimized.

## 2. Definitions
*   **Hopper**: A semi-infinite rectangle with fixed width and variable height.
*   **Nesting**: The process of arranging irregular shapes to minimize waste.
*   **No-Fit Polygon (NFP)**: A geometric structure that represents all relative positions where two polygons touch without overlapping.
*   **Gravity Heuristic**: A strategy where polygons are "dropped" into the hopper and slide as far down and left as possible.

## 3. Theory
The core of hopper optimization is determining the **feasible placement** of a new polygon $P_{new}$ relative to already placed polygons $\{P_1, \dots, P_k\}$.
1.  **NFP Calculation**: For every pair of polygons $(P_i, P_{new})$, the No-Fit Polygon $NFP_{i,new}$ is computed. This polygon defines the forbidden region for the reference point of $P_{new}$.
2.  **Feasible Space**: The set of all possible positions for $P_{new}$ is the area inside the hopper minus the union of all $NFPs$.
3.  **Optimization**: The algorithm searches for a position in the feasible space that minimizes the current maximum height of the packing.

A common approach is the **Bottom-Left-Fill (BLF)** heuristic, which always places the next polygon at the lowest and then leftmost available position.

## 4. Pseudo code
```python
function HopperOptimize(hopper_width, polygons):
    # 1. Sort polygons by a heuristic (e.g., Area descending)
    polygons.sort(key=lambda p: p.area, reverse=True)
    
    placed_polygons = []
    
    for p_new in polygons:
        # 2. Find the lowest feasible position
        # Start at the top of the current packing
        best_pos = FindLowestPosition(p_new, placed_polygons, hopper_width)
        
        # 3. Update the packing
        p_new.position = best_pos
        placed_polygons.append(p_new)
        
    return GetMaxHeight(placed_polygons)

function FindLowestPosition(p_new, placed, width):
    # Uses NFPs to identify the boundary of the 'forbidden' region
    forbidden_region = Union([ComputeNFP(p_i, p_new) for p_i in placed])
    
    # Search the boundary of the forbidden region for the min-y point
    # that is within the hopper width [0, width - p_new.width]
    return min(forbidden_region.boundary, key=lambda p: (p.y, p.x))
```

## 5. Parameters Selections
*   **Sorting Rule**: Decreasing area or decreasing height are standard.
*   **Rotation**: Allowing discrete rotations (e.g., $0^\circ, 90^\circ, 180^\circ, 270^\circ$) or continuous rotation significantly improves results but increases complexity.
*   **NFP Precision**: For complex curved shapes, polygons are often simplified or sampled.

## 6. Complexity
*   **NFP Calculation**: $O(n \cdot m)$ for two convex polygons with $n$ and $m$ vertices. For non-convex, it can be much higher.
*   **Packing Heuristic**: $O(k^2)$ where $k$ is the number of polygons, assuming NFP lookups are optimized.

## 7. Usages
*   **Textile Industry**: Nesting clothing patterns onto a roll of fabric.
*   **Sheet Metal Cutting**: Arranging mechanical parts on a metal plate for laser or waterjet cutting.
*   **Leather Industry**: Packing parts onto irregular animal hides (which includes avoiding defects).
*   **Shipbuilding**: Cutting large steel plates for hulls.
*   **Furniture Manufacturing**: Maximizing the use of plywood or wood planks.

## 8. Testing methods and Edge cases
*   **Convex vs. Non-Convex**: Verify that the algorithm handles interlocking U-shapes or L-shapes correctly.
*   **Container Width**: Ensure no polygon extends beyond the hopper walls.
*   **Overlap Check**: Rigorous verification that no two polygons intersect.
*   **Hopper Height**: The primary metric to minimize.
*   **Large Quantity**: Test with hundreds of small pieces to ensure stability.

## 9. References
*   Bennell, J. A., & Oliveira, J. F. (2008). "The geometry of nesting problems: A tutorial". European Journal of Operational Research.
*   Burke, E. K., Hellier, R. S., Kendall, G., & Whitwell, G. (2007). "Complete and robust no-fit polygon generation for the irregular cutting and packing problem". European Journal of Operational Research.
*   Wikipedia: [Nesting (process)](https://en.wikipedia.org/wiki/Nesting_(process))
