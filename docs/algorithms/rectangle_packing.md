# Rectangle Packing

## 1. Overview
Rectangle packing is the problem of arranging a set of rectangles of varying sizes within a larger container rectangle such that no two rectangles overlap and the total wasted space is minimized (or the density is maximized). This is a classic NP-hard optimization problem with wide-ranging applications in manufacturing, logistics, and computer graphics.

## 2. Definitions
*   **Bin Packing**: The problem of packing objects into multiple bins of fixed size.
*   **Strip Packing**: Packing rectangles into a container with a fixed width and infinite height, minimizing the height used.
*   **Guillotine Cut**: A cut that goes entirely from one edge of a rectangle to the opposite edge in a straight line.
*   **Skyline**: A representation of the "top edge" of the current packing, used to find placement locations.

## 3. Theory
Because rectangle packing is NP-hard, heuristic and metaheuristic algorithms are used in practice.
1.  **Shelf Algorithms**: Rectangles are placed in "shelves" (rows). When a rectangle doesn't fit in the current shelf, a new shelf is started above it. (e.g., Next-Fit Decreasing Height).
2.  **Guillotine Algorithms**: The container is recursively split into two smaller rectangles using horizontal or vertical cuts.
3.  **MaxRects**: Maintains a list of all maximal free rectangular areas. A new rectangle is placed into one of these areas, and the remaining free spaces are recalculated.
4.  **Skyline Algorithms**: Tracks the top boundary of the packed rectangles. New rectangles are placed on the lowest part of the skyline.

Sorting the rectangles by height or area before packing (e.g., First-Fit Decreasing) significantly improves the performance of most heuristics.

## 4. Pseudo code
### MaxRects (BSSF - Best Short Side Fit)
```python
function MaxRects(bin_width, bin_height, rectangles):
    # 1. Initialize free list with the whole bin
    free_rects = [Rectangle(0, 0, bin_width, bin_height)]
    placed_rects = []
    
    # Sort input by height descending (common heuristic)
    rectangles.sort(key=lambda r: r.h, reverse=True)
    
    for r in rectangles:
        # 2. Find best free rectangle to place current one
        best_fit = None
        min_short_side_fit = infinity
        
        for f in free_rects:
            if f.w >= r.w and f.h >= r.h:
                fit = min(f.w - r.w, f.h - r.h)
                if fit < min_short_side_fit:
                    min_short_side_fit = fit
                    best_fit = f
                    
        if best_fit is not None:
            # 3. Place rectangle
            r.x, r.y = best_fit.x, best_fit.y
            placed_rects.append(r)
            
            # 4. Split and update free list
            new_free = []
            for f in free_rects:
                new_free.extend(SplitFreeRect(f, r))
            free_rects = PruneRedundant(new_free)
            
    return placed_rects
```

## 5. Parameters Selections
*   **Rotation**: Allowing $90^\circ$ rotation can significantly increase packing density.
*   **Heuristic Choice**: **MaxRects** is generally considered the best-performing heuristic for 2D packing, while **Guillotine** is faster but less efficient.

## 6. Complexity
*   **Heuristic Packing**: $O(n^2)$ for simple heuristics like First-Fit. MaxRects can be $O(n^3)$ in the worst case as the free list grows.
*   **Optimal Packing**: Exponential $O(2^n)$, only feasible for small $n$ (e.g., $n < 20$).

## 7. Usages
*   **Manufacturing**: Cutting parts from a sheet of wood, metal, or fabric (Nestling).
*   **Sprite Sheet Generation**: Packing many small game icons into a single large texture to improve GPU performance.
*   **Logistics**: Loading pallets or shipping containers.
*   **UI Layout**: Arranging windows or widgets in a tile-based interface.
*   **VLSI Design**: Floorplanning of electronic components on a chip.

## 8. Testing methods and Edge cases
*   **Overlap Check**: Verify that no two rectangles in the final layout intersect.
*   **Container Boundary**: Ensure all rectangles are within the bin.
*   **Density Calculation**: Calculate (Total Rectangle Area) / (Container Area).
*   **Large Rectangles**: Test cases where one rectangle takes up most of the bin.
*   **Thin Rectangles**: Test "sliver" rectangles that are hard to pack.
*   **Rotation**: Verify that rotating a rectangle $90^\circ$ is handled correctly by the splitting logic.

## 9. References
*   Jylänki, J. (2010). "A Thousand Ways to Pack the Bin - A Practical Approach to Two-Dimensional Rectangle Bin Packing". Technical Report.
*   Lodi, A., Martello, S., & Monaci, M. (2002). "Two-dimensional packing problems: A survey". European Journal of Operational Research.
*   Wikipedia: [Packing problems](https://en.wikipedia.org/wiki/Packing_problems)
