# Spiral Walk

## 1. Overview
A spiral walk is a space-filling traversal that starts at a center point and visits cells in a 2D grid in an expanding spiral pattern. Unlike Hilbert or Morton curves, which are recursive and locality-preserving, the spiral walk is intuitive and ensures that the distance from the starting point increases monotonically (on average). It is used for localized searching, image scanning, and data visualization.

## 2. Definitions
*   **Archimedean Spiral**: A continuous curve where the distance from the origin is proportional to the angle.
*   **Square Spiral**: A discrete version of the spiral restricted to a square grid.
*   **Radius (r)**: The maximum Manhattan or Chebyshev distance from the starting point during the walk.

## 3. Theory
The square spiral walk is typically performed by moving in layers.
1.  **Layer 0**: The starting cell $(0,0)$.
2.  **Layer 1**: The 8 neighbors surrounding the center.
3.  **Layer k**: The $8k$ cells that form the perimeter of a $(2k+1) \times (2k+1)$ square.

The walk follows a repeating pattern of directions (e.g., Right, Up, Left, Down) with increasing segment lengths. For example:
*   Right 1, Up 1
*   Left 2, Down 2
*   Right 3, Up 3
*   Left 4, Down 4
*   ...

## 4. Pseudo code
```python
function SpiralWalk(num_steps):
    x, y = 0, 0
    path = [(x, y)]
    
    # Directions: Right, Up, Left, Down
    dx = [1, 0, -1, 0]
    dy = [0, 1, 0, -1]
    
    step_limit = 1
    direction = 0
    
    while len(path) < num_steps:
        # Move in current direction for 'step_limit' steps
        for _ in range(2): # Two directions share the same limit
            for _ in range(step_limit):
                if len(path) >= num_steps: break
                x += dx[direction]
                y += dy[direction]
                path.append((x, y))
            
            # Change direction
            direction = (direction + 1) % 4
            
        # Increase segment length after every two turns
        step_limit += 1
        
    return path
```

## 5. Parameters Selections
*   **Starting Direction**: Can be any of the four cardinal directions.
*   **Orientation**: Clockwise vs. Counter-clockwise.
*   **Step Size**: Standard is 1 unit, but can be larger for sparse sampling.

## 6. Complexity
*   **Time Complexity**: $O(n)$ where $n$ is the number of steps.
*   **Space Complexity**: $O(n)$ to store the path coordinates.

## 7. Usages
*   **Search Algorithms**: Finding the nearest point of interest starting from a query location (e.g., "nearest gas station" in a local grid).
*   **Computer Vision**: Scanning a local neighborhood around a keypoint or feature.
*   **Procedural Generation**: Growing a city or a structure from a central "seed" location.
*   **Data Visualization**: Arranging objects around a center based on their priority or timestamp (e.g., a "spiral timeline").
*   **Cryptography**: Permuting bits or pixels in a non-linear but deterministic way.

## 8. Testing methods and Edge cases
*   **Full Coverage**: Verify that every $(x, y)$ coordinate within a $k$-layer square is visited exactly once.
*   **Monotonicity**: Ensure that for any two sequential points $P_i, P_{i+1}$, their coordinates change by exactly 1 unit.
*   **Large Step Count**: Verify the coordinates don't drift or skip cells for $n > 10^6$.
*   **Start at Edge**: Handle cases where the spiral is constrained within a bounding box and must stop at the edges.

## 9. References
*   Stein, M. L., Ulam, S. M., & Wells, M. B. (1964). "A Visual Display of Some Properties of the Distribution of Primes". The American Mathematical Monthly. (The Ulam Spiral).
*   Gardner, M. (1971). "The Extraordinary Properties of the Mathematical Constant Pi". Scientific American.
*   Wikipedia: [Spiral](https://en.wikipedia.org/wiki/Spiral)
