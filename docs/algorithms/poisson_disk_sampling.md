# Poisson Disk Sampling

## 1. Overview
Poisson disk sampling is a technique for generating a set of points in a multidimensional space such that no two points are closer to each other than a specified minimum distance $r$. The resulting distribution has a "blue noise" characteristic: the points are tightly packed but avoid the structured look of a grid and the clumping found in pure random (white noise) sampling. This makes it ideal for computer graphics, procedural generation, and sensor placement.

## 2. Definitions
*   **Minimum Distance (r)**: The radius of an exclusion disk around each point.
*   **Blue Noise**: A random distribution where low-frequency components are minimized, resulting in a visually pleasing and uniform distribution.
*   **Bridson's Algorithm**: A fast $O(n)$ algorithm for generating Poisson disk samples in any dimension.
*   **Rejection Sampling**: A naive approach where random points are generated and discarded if they fall within distance $r$ of any existing point.

## 3. Theory
Bridson's algorithm is the standard for efficient Poisson disk sampling:
1.  **Initialize**: Place an initial point randomly in the domain and add it to an **active list**.
2.  **Grid**: Initialize a background grid with cell size $r / \sqrt{d}$ (where $d$ is dimension) to ensure each cell can contain at most one point.
3.  **Active Sampling**: While the active list is not empty:
    *   Pick a random point $P$ from the active list.
    *   Generate up to $k$ candidates in an annulus $[r, 2r]$ around $P$.
    *   For each candidate $Q$, check if it is within distance $r$ of any existing points (using the grid for $O(1)$ lookups).
    *   If $Q$ is valid, add it to the grid and the active list.
    *   If no candidates are found after $k$ trials, remove $P$ from the active list.

## 4. Pseudo code
```python
function PoissonDiskSampling(width, height, r, k=30):
    # 1. Initialize Grid
    cell_size = r / sqrt(2)
    cols = ceil(width / cell_size)
    rows = ceil(height / cell_size)
    grid = array[cols][rows] initialized to None
    
    # 2. Seed Point
    start_p = Point(random(width), random(height))
    active_list = [start_p]
    InsertIntoGrid(start_p, grid, cell_size)
    
    points = [start_p]
    
    # 3. Main Loop
    while active_list:
        p = random.choice(active_list)
        found = False
        
        for _ in range(k):
            # Generate candidate in annulus [r, 2r]
            q = GenerateRandomInAnnulus(p, r, 2*r)
            
            if IsInBounds(q, width, height) and IsValid(q, grid, r, cell_size):
                points.append(q)
                active_list.append(q)
                InsertIntoGrid(q, grid, cell_size)
                found = True
                break
                
        if not found:
            active_list.remove(p)
            
    return points
```

## 5. Parameters Selections
*   **Radius (r)**: Determines the density of the points.
*   **Trials (k)**: Typically set to 30. Higher $k$ results in tighter packing but increases computation time.
*   **Variable Radius**: The algorithm can be adapted to use a varying $r(x, y)$ based on an importance map or image brightness.

## 6. Complexity
*   **Time Complexity**: $O(n)$ where $n$ is the number of points generated, thanks to the grid-based spatial lookup.
*   **Space Complexity**: $O(n)$ to store the points and the grid.

## 7. Usages
*   **Computer Graphics**: Placing objects (like trees or grass) in a natural-looking distribution.
*   **Rendering**: Anti-aliasing and jittered sampling for ray tracing.
*   **Image Processing**: Halftoning and stippling (representing an image with dots).
*   **Procedural Content Generation**: Generating city layouts or dungeon rooms.
*   **Physical Simulation**: Initializing particles for fluid or granular simulations.

## 8. Testing methods and Edge cases
*   **Distance Constraint**: Verify that for all pairs $(P_i, P_j)$, $dist(P_i, P_j) \ge r$.
*   **Boundary Handling**: Ensure points are correctly generated near the edges of the domain.
*   **Clumping**: Check the Fourier transform of the point set to verify the blue noise profile (lack of low-frequency spikes).
*   **Empty Result**: If the domain is smaller than $r$, the algorithm should return at most one point.
*   **Grid Overflow**: Ensure the grid coordinates are correctly clamped to the array bounds.

## 9. References
*   Bridson, R. (2007). "Fast Poisson disk sampling in arbitrary dimensions". SIGGRAPH Sketches.
*   Cook, R. L. (1986). "Stochastic sampling in computer graphics". ACM Transactions on Graphics.
*   Lagae, A., & Dutré, P. (2008). "A comparison of methods for generating Poisson disk distributions". Computer Graphics Forum.
*   Wikipedia: [Poisson disk sampling](https://en.wikipedia.org/wiki/Poisson_disk_sampling)
