# Affine Heat Flow (Polygon Smoothing)

## 1. Overview
Affine heat flow is a geometric smoothing process for polygons and curves that is invariant under affine transformations (rotation, scaling, translation, and shearing). While standard heat flow (curve shortening flow) tends to evolve shapes toward circles, affine heat flow evolves them toward ellipses. It is used in image processing and computer vision for shape simplification and denoising where the affine structure of the object must be preserved.

## 2. Definitions
*   **Heat Flow**: The process of moving each point on a boundary in the direction of its normal with a speed proportional to its curvature.
*   **Affine Invariance**: A property where the result of the flow on a transformed shape is the same as the transformation applied to the flow result.
*   **Euclidean Curvature ($\kappa$)**: The standard rate of change of the tangent direction.
*   **Affine Curvature**: A more complex measure of curvature that remains unchanged under affine maps.

## 3. Theory
Standard curve shortening flow is defined by $\frac{\partial P}{\partial t} = \kappa \mathbf{N}$. 
Affine heat flow is defined by $\frac{\partial P}{\partial t} = \kappa^{1/3} \mathbf{N}$. 

This specific power of $1/3$ is what provides the affine invariance. In the discrete case (for polygons), the flow is often implemented by iteratively updating vertex positions using a weighted average of their neighbors, but with weights that account for the local area or affine metric.

A common discrete approximation for a vertex $V_i$ with neighbors $V_{i-1}$ and $V_{i+1}$ is:
$$V_i^{new} = V_i + \Delta t \cdot \text{Area}(V_{i-1}, V_i, V_{i+1})^{1/3} \cdot \mathbf{N}_i$$
where $\mathbf{N}_i$ is the discrete normal vector.

## 4. Pseudo code
```python
function AffinePolygonSmoothing(polygon, dt, iterations):
    current_vertices = polygon.vertices
    
    for _ in range(iterations):
        new_vertices = []
        n = len(current_vertices)
        
        for i in range(n):
            v_prev = current_vertices[(i - 1) % n]
            v_curr = current_vertices[i]
            v_next = current_vertices[(i + 1) % n]
            
            # 1. Calculate local vectors
            edge1 = v_curr - v_prev
            edge2 = v_next - v_curr
            
            # 2. Calculate signed area (proportional to curvature)
            area = 0.5 * abs(cross_product(edge1, edge2))
            
            # 3. Calculate normal direction (simplified)
            # Bisector of the angle
            normal = Normalize(Perpendicular(edge2) + Perpendicular(edge1))
            
            # 4. Update vertex position with 1/3 power
            displacement = (area ** (1/3)) * normal * dt
            new_vertices.append(v_curr + displacement)
            
        current_vertices = new_vertices
        
    return Polygon(current_vertices)
```

## 5. Parameters Selections
*   **Time Step ($dt$ )**: Must be small enough to ensure stability (CFL condition).
*   **Iterations**: More iterations result in smoother, more simplified shapes.
*   **Area Threshold**: Small areas (near-collinear vertices) can lead to numerical instability; an epsilon threshold is often used.

## 6. Complexity
*   **Time Complexity**: $O(I \cdot n)$ where $I$ is iterations and $n$ is vertex count.
*   **Space Complexity**: $O(n)$ to store the vertex positions.

## 7. Usages
*   **Shape Recognition**: Normalizing shapes to a "canonical" form before matching in a database.
*   **Computer Vision**: Preprocessing object silhouettes to remove pixelation or noise while preserving geometric structure.
*   **Cartography**: Simplifying coastlines or boundaries for small-scale maps.
*   **Generative Design**: Creating organic, smooth shapes from rough polyline sketches.
*   **Image Analysis**: Analyzing the "affine scale space" of an image.

## 8. Testing methods and Edge cases
*   **Ellipses**: An ellipse should remain an ellipse under affine heat flow (only its size should change).
*   **Squares**: A square should gradually round its corners and evolve toward an ellipse.
*   **Affine Symmetry**: Verify that shearing a polygon, smoothing it, and then "un-shearing" it gives the same result as smoothing the original polygon.
*   **Self-Intersections**: Ensure the flow doesn't cause the polygon to cross itself (though this is theoretically possible for non-convex shapes).
*   **Zero Area**: Handle perfectly collinear triplets of vertices.

## 9. References
*   Sapiro, G., & Tannenbaum, A. (1993). "Affine invariant scale-space". International Journal of Computer Vision.
*   Olver, P. J., Sapiro, G., & Tannenbaum, A. (1994). "Affine invariant geometric evolutions of planar curves". SIAM Journal on Applied Mathematics.
*   Angenent, S., Sapiro, G., & Tannenbaum, A. (1998). "On the affine heat equation for non-convex curves". Journal of the American Mathematical Society.
*   Wikipedia: [Affine shape adaptation](https://en.wikipedia.org/wiki/Affine_shape_adaptation)
