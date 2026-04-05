# Polygonal Mean Curvature Flow (Smoothing)

## 1. Overview
Polygonal Mean Curvature Flow is a geometric process used to smooth the boundaries of a polygon. It is a discrete version of the curve-shortening flow, where each point on a curve moves in the direction of its curvature vector. Over time, this process eliminates high-frequency noise and sharp corners, causing the polygon to become smoother and more circular.

## 2. Definitions
*   **Mean Curvature**: In the context of curves, this is the rate at which the tangent direction changes along the curve.
*   **Discrete Laplacian**: An operator that approximates the second derivative of the vertex positions. For a vertex $V_i$, it is defined as $L_i = V_{i-1} - 2V_i + V_{i+1}$.
*   **Time Step ($\Delta t$ )**: A parameter controlling the magnitude of displacement in each iteration.
*   **Centroid**: The geometric center of the polygon.

## 3. Theory
The flow is based on the diffusion equation (heat equation) applied to geometry: $\frac{\partial P}{\partial t} = \Delta P$. In a discrete polygon, moving a vertex $V_i$ by its Laplacian is equivalent to moving it toward the midpoint of its two neighbors ($V_{i-1}$ and $V_{i+1}$). This local averaging effect reduces the "sharpness" of vertices. 

A known property of this flow is that any simple closed curve will eventually become convex and then shrink to a circular point (the Gage-Hamilton-Grayson theorem). To use this for smoothing without losing the shape entirely, the process is usually limited to a few iterations or includes a scaling step to preserve the original perimeter or area.

## 4. Pseudo code
```python
function MeanCurvatureFlow(polygon, iterations, dt, preserve_size):
    n = len(polygon)
    current = polygon
    original_perimeter = CalculatePerimeter(polygon)
    
    for k in range(iterations):
        next_gen = []
        for i in range(n):
            # Compute discrete Laplacian
            L_x = current[i-1].x - 2*current[i].x + current[i+1].x
            L_y = current[i-1].y - 2*current[i].y + current[i+1].y
            
            # Move vertex
            new_x = current[i].x + dt * L_x
            new_y = current[i].y + dt * L_y
            next_gen.append(Point(new_x, new_y))
            
        if preserve_size:
            current_perimeter = CalculatePerimeter(next_gen)
            scale = original_perimeter / current_perimeter
            next_gen = Scale(next_gen, scale)
            
        current = next_gen
        
    return current
```

## 5. Parameters Selections
*   **Time Step ($\Delta t$ )**: Typically set between 0.01 and 0.2. Values above 0.5 can lead to numerical instability where the polygon "explodes."
*   **Iterations**: Depends on the level of noise. Usually 10–100 steps are sufficient for smoothing.
*   **Preservation**: `keep_perimeter` or `keep_area` prevents the polygon from shrinking to a point.

## 6. Complexity
*   **Time Complexity**: $O(n \cdot i)$, where $n$ is the number of vertices and $i$ is the number of iterations.
*   **Space Complexity**: $O(n)$ to store the vertex positions.

## 7. Usages
*   **Image Processing**: Smoothing the results of contour extraction.
*   **GIS**: Generalizing map boundaries for different zoom levels.
*   **Computer Graphics**: Creating organic-looking shapes from blocky initial geometry.
*   **CAD**: Removing artifacts from digitized or scanned blueprints.

## 8. Testing methods and Edge cases
*   **Jagged Input**: Verify that "zig-zag" patterns are flattened.
*   **Stability**: Test with large $\Delta t$ to identify the breaking point.
*   **Self-intersection**: Check if the flow resolves or creates new self-intersections.
*   **Collinear Vertices**: Verify that straight edges remain straight.
*   **Drift**: Ensure the centroid remains relatively stationary if re-centering is applied.

## 9. References
*   Gage, M., & Hamilton, R. S. (1986). "The heat equation shrinking convex plane curves". Journal of Differential Geometry.
*   Grayson, M. A. (1987). "The heat equation shrinks embedded plane curves to round points". Journal of Differential Geometry.
*   Desbrun, M., Meyer, M., Schröder, P., & Barr, A. H. (1999). "Implicit fairing of irregular meshes using diffusion and curvature flow". SIGGRAPH.
*   [Wikipedia: Curve-shortening flow](https://en.wikipedia.org/wiki/Curve-shortening_flow)
