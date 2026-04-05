# Ear Clipping (Polygon Triangulation)

## 1. Overview
Ear clipping is a simple and intuitive algorithm for triangulating a simple polygon. It is based on the Two-Ears Theorem, which states that every simple polygon with at least four vertices has at least two "ears" that can be removed to form a smaller simple polygon. By repeatedly clipping these ears, the entire polygon is eventually decomposed into triangles.

## 2. Definitions
*   **Simple Polygon**: A polygon that does not self-intersect and has no holes.
*   **Convex Vertex**: A vertex where the internal angle is less than 180 degrees.
*   **Ear**: A vertex $V_i$ is an ear if the triangle formed by $V_{i-1}, V_i, V_{i+1}$ is entirely within the polygon and contains no other vertices of the polygon.
*   **Barycentric Coordinates**: A coordinate system used to determine if a point lies inside a triangle.

## 3. Theory
The algorithm proceeds by identifying a vertex that satisfies two conditions:
1.  The vertex is **convex** (the turn from $V_{i-1}$ to $V_i$ to $V_{i+1}$ is counter-clockwise for CCW polygons).
2.  The triangle formed by $V_{i-1}, V_i, V_{i+1}$ contains no other vertices of the polygon in its interior.

Once such an ear is found, the triangle $(V_{i-1}, V_i, V_{i+1})$ is recorded, and the vertex $V_i$ is removed from the polygon's vertex list. This process is repeated until only three vertices remain, which form the final triangle.

## 4. Pseudo code
```python
function Triangulate(polygon):
    indices = list of vertex indices [0, 1, ..., n-1]
    triangles = []
    
    while len(indices) > 3:
        for i in range(len(indices)):
            u = indices[i-1]
            v = indices[i]
            w = indices[(i+1) % len(indices)]
            
            if IsEar(u, v, w, indices, polygon):
                triangles.append((u, v, w))
                indices.pop(i)
                break # Start searching again from the new polygon
                
    # Add the last remaining triangle
    triangles.append(tuple(indices))
    return triangles

function IsEar(u, v, w, current_indices, polygon):
    # 1. Check if the vertex is convex
    if cross_product(polygon[u], polygon[v], polygon[w]) <= 0:
        return False
        
    # 2. Check if any other vertex lies inside the triangle (u, v, w)
    for index in current_indices:
        if index in (u, v, w): continue
        if PointInTriangle(polygon[index], polygon[u], polygon[v], polygon[w]):
            return False
            
    return True
```

## 5. Parameters Selections
*   **Input**: A list of `Point2D` representing a simple polygon in counter-clockwise order.
*   **Precision**: An epsilon should be used in cross-product and point-in-triangle tests to handle floating-point inaccuracies.

## 6. Complexity
*   **Time Complexity**: $O(n^2)$ for a polygon with $n$ vertices. In each step, we check $O(n)$ vertices for "ear-ness," and each check takes $O(n)$ time to verify that no other points are inside.
*   **Space Complexity**: $O(n)$ to store the triangles and the remaining vertex indices.

## 7. Usages
*   Converting arbitrary polygons into triangles for rendering via OpenGL or DirectX.
*   Preprocessing geometry for physics simulation and collision detection.
*   Calculating the area or centroid of complex shapes.

## 8. Testing methods and Edge cases
*   **Concave Polygons**: Ensure the algorithm correctly skips reflex (non-convex) vertices.
*   **Collinear Vertices**: Handled by strict inequality in the convexity check.
*   **Self-intersecting Polygons**: Basic ear clipping may fail or produce incorrect results; the input must be simple.
*   **Sliver Triangles**: Very thin polygons can lead to numerical stability issues.
*   **Degenerate Polygons**: Polygons with 0, 1, or 2 vertices.

## 9. References
*   Meisters, G. H. (1975). "Polygons have ears". The American Mathematical Monthly.
*   Eberly, D. (2002). "Triangulation by Ear Clipping". Geometric Tools.
*   [Wikipedia: Polygon triangulation](https://en.wikipedia.org/wiki/Polygon_triangulation)
