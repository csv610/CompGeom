# Fast Marching Method

## 1. Overview
The Fast Marching Method (FMM) is a numerical technique for solving the **Eikonal equation**, a non-linear first-order partial differential equation that describes the evolution of a wave front. It is used to compute the shortest travel time (or distance) from a source point to all other points in a domain, even when the "speed" of travel varies across space. It can be viewed as a continuous version of Dijkstra's algorithm.

## 2. Definitions
*   **Eikonal Equation**: $|\nabla u(x)| = F(x)$, where $u(x)$ is the arrival time and $F(x)$ is the reciprocal of the speed at point $x$.
*   **Isotropic Speed**: Speed $F(x)$ that depends only on location, not on the direction of travel.
*   **Wave Front**: A level set of the time function $u(x) = C$.
*   **Upwind Scheme**: A numerical discretization where the solution at a point is computed using values from "upstream" (where the time is smaller).

## 3. Theory
FMM simulates the propagation of a front by moving from points where the travel time is already known to points where it is unknown. To maintain efficiency, points are categorized into three sets:
1.  **Accepted**: Points where the time is correctly calculated and fixed.
2.  **Trial**: Points on the boundary of the Accepted set; their times are estimated and kept in a priority queue.
3.  **Far**: Points that have not been reached yet.

The key to FMM is the **upwind discretization** of the gradient $|\nabla u|$. In 2D, on a Cartesian grid with spacing $h$, the discretization is:
$$\max(D^{-x}_{ij}u, -D^{+x}_{ij}u, 0)^2 + \max(D^{-y}_{ij}u, -D^{+y}_{ij}u, 0)^2 = F_{ij}^2$$
where $D$ represents the finite difference operators. This quadratic equation ensures that the "information" only flows from regions of smaller $u$ to regions of larger $u$.

## 4. Pseudo code
```python
function FastMarching(source, speed_field):
    # 1. Initialization
    U = Array(infinity)
    status = Array(FAR)
    
    U[source] = 0
    status[source] = ACCEPTED
    
    # 2. Add neighbors of source to TRIAL set
    trial_queue = PriorityQueue()
    for neighbor in GetNeighbors(source):
        U[neighbor] = CalculateEikonal(neighbor, U, speed_field)
        status[neighbor] = TRIAL
        trial_queue.push(neighbor, U[neighbor])
        
    # 3. Main Loop
    while not trial_queue.empty():
        # Get point with minimum estimated time
        p = trial_queue.pop_min()
        status[p] = ACCEPTED
        
        # Update neighbors of the newly accepted point
        for neighbor in GetNeighbors(p):
            if status[neighbor] == ACCEPTED: continue
            
            # Solve quadratic for the neighbor
            old_val = U[neighbor]
            new_val = CalculateEikonal(neighbor, U, speed_field)
            
            if status[neighbor] == FAR:
                U[neighbor] = new_val
                status[neighbor] = TRIAL
                trial_queue.push(neighbor, new_val)
            elif new_val < old_val:
                U[neighbor] = new_val
                trial_queue.update_priority(neighbor, new_val)
                
    return U
```

## 5. Parameters Selections
*   **Grid Resolution**: Finer grids produce more accurate wave fronts but require more memory and time.
*   **Speed Function ($F$)**: Can be constant ($1.0$ for Euclidean distance) or varying (to simulate terrain or obstacles).
*   **Solver Order**: First-order FMM is standard; higher-order versions use more neighbors to achieve better accuracy.

## 6. Complexity
*   **Time Complexity**: $O(N \log N)$ where $N$ is the number of grid points, due to the priority queue operations.
*   **Space Complexity**: $O(N)$ to store the travel times and the status of each point.

## 7. Usages
*   **Geodesic Distance on Meshes**: Computing distances along a surface (e.g., finding the shortest path over a mountain).
*   **Image Segmentation**: Active contours (snakes) that expand to find object boundaries.
*   **Robotics**: Path planning in complex environments with different "terrains" (e.g., water vs. land).
*   **Medical Imaging**: Bone or organ segmentation in CT/MRI scans.
*   **Seismology**: Simulating earthquake wave propagation.

## 8. Testing methods and Edge cases
*   **Constant Speed**: The resulting time field should be exactly proportional to the Euclidean distance from the source.
*   **Obstacles**: Set speed to zero (or $F \to \infty$) at obstacles; the front should flow around them.
*   **Varying Speed**: Use a simple linear speed gradient to verify that the front bends (refraction) correctly according to Snell's law.
*   **Grid Boundaries**: Ensure the algorithm handles the edges of the domain without crashing.
*   **Multiple Sources**: Initialize multiple points to 0; the result should be a Voronoi-like partition of arrival times.

## 9. References
*   Sethian, J. A. (1996). "A fast marching level set method for monotonically advancing fronts". Proceedings of the National Academy of Sciences.
*   Tsitsiklis, J. N. (1995). "Efficient algorithms for globally optimal trajectories". IEEE Transactions on Automatic Control.
*   Kimmel, R., & Sethian, J. A. (1998). "Computing geodesic paths on manifolds". Proceedings of the National Academy of Sciences.
*   Wikipedia: [Fast marching method](https://en.wikipedia.org/wiki/Fast_marching_method)
