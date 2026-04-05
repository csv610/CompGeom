# Random Walk

## 1. Overview
A random walk is a mathematical object, known as a stochastic or random process, that describes a path consisting of a succession of random steps on some mathematical space such as the integers or a 2D/3D grid. In computational geometry and physics, random walks are used to model diffusion, Brownian motion, and to approximate the solutions of various partial differential equations (PDEs) through Monte Carlo methods.

## 2. Definitions
*   **Step Size ($\ell$)**: The distance moved in a single step.
*   **Lattice Walk**: A random walk restricted to a discrete grid (e.g., integer coordinates).
*   **Isotropic Walk**: A walk where every direction is equally likely.
*   **Mean Squared Displacement (MSD)**: A measure of how far the walker deviates from its starting point over time. For a simple random walk, $MSD \propto t$.

## 3. Theory
The theory of random walks is closely related to the **diffusion equation** $\frac{\partial \phi}{\partial t} = D \nabla^2 \phi$.
1.  **1D Walk**: A walker starts at 0 and moves +1 or -1 with probability $1/2$. After $n$ steps, the expected position is 0, but the standard deviation is $\sqrt{n}$.
2.  **2D/3D Walk**: The walker moves in a random direction. Polya's Theorem states that a random walk on a 2D lattice is "recurrent" (it will return to the start with probability 1), while in 3D it is "transient" (it may never return).
3.  **Walk on Meshes**: A random walk on a mesh jumps from a vertex to one of its adjacent vertices. The probability of choosing a neighbor can be uniform ($1/degree$) or weighted by edge length or cotangent weights to simulate specific geometric properties.

## 4. Pseudo code
### Simple 2D Random Walk (Continuous)
```python
function RandomWalk2D(start_point, num_steps, step_size):
    current = start_point
    path = [current]
    
    for i in range(num_steps):
        # 1. Choose random direction
        theta = random.uniform(0, 2 * pi)
        
        # 2. Update position
        dx = step_size * cos(theta)
        dy = step_size * sin(theta)
        current = Point(current.x + dx, current.y + dy)
        
        path.append(current)
        
    return path
```

### Random Walk on a Mesh
```python
function MeshRandomWalk(mesh, start_v, num_steps):
    current_v = start_v
    visited_v = [current_v]
    
    for i in range(num_steps):
        neighbors = mesh.GetNeighbors(current_v)
        # 1. Choose a random neighbor
        current_v = random.choice(neighbors)
        visited_v.append(current_v)
        
    return visited_v
```

## 5. Parameters Selections
*   **Step Size**: Constant step size vs. variable (Gaussian) step size.
*   **Connectivity**: On a grid, 4-connectivity (von Neumann) vs. 8-connectivity (Moore).
*   **Weights**: In weighted random walks, the probability of a step is proportional to some value (e.g., $e^{-\Delta E / kT}$).

## 6. Complexity
*   **Time Complexity**: $O(n)$ where $n$ is the number of steps.
*   **Space Complexity**: $O(n)$ to store the full path, or $O(1)$ if only the final position is needed.

## 7. Usages
*   **Monte Carlo Simulation**: Estimating areas or volumes of complex shapes (Hit-or-Miss Monte Carlo).
*   **Mesh Analysis**: Using random walks to calculate "closeness" between vertices or to partition meshes.
*   **Generative Art**: Creating organic, branching patterns (e.g., Diffusion-Limited Aggregation).
*   **Network Science**: Identifying communities in a graph or calculating PageRank.
*   **Finance**: Modeling stock price movements (Geometric Brownian Motion).
*   **Physics**: Simulating the movement of gas particles or the propagation of heat.

## 8. Testing methods and Edge cases
*   **Mean Position**: Verify that after many trials, the average final position of an isotropic walk is the starting point.
*   **Scaling Law**: Verify that the distance from the start grows as $\sqrt{n}$ on average.
*   **Boundaries**: Test how the walk behaves when it hits a wall (e.g., reflection vs. absorption).
*   **Mesh Boundaries**: Ensure the walker doesn't "fall off" the edge of an open mesh.
*   **Looping**: Observe how often the walker visits the same vertex in 2D vs 3D.

## 9. References
*   Pearson, K. (1905). "The Problem of the Random Walk". Nature.
*   Polya, G. (1921). "Über eine Aufgabe der Wahrscheinlichkeitsrechnung betreffend die Irrfahrt im Straßennetz". Mathematische Annalen.
*   Spitzer, F. (1976). "Principles of Random Walk". Springer.
*   Wikipedia: [Random walk](https://en.wikipedia.org/wiki/Random_walk)
