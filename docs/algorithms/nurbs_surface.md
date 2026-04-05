# NURBS Surface Evaluation

## 1. Overview
NURBS (Non-Uniform Rational B-Splines) are a mathematical model commonly used in computer graphics and computer-aided design (CAD) for generating and representing curves and surfaces. NURBS surfaces provide a highly flexible and unified way to represent both analytic shapes (like spheres, cones, and cylinders) and complex, free-form organic shapes. Evaluating a NURBS surface involves calculating the 3D coordinates $(x, y, z)$ at a given parameter pair $(u, v)$ within the surface's domain.

## 2. Definitions
*   **Knot Vector**: A non-decreasing sequence of real numbers that determines how the control points affect the NURBS surface.
*   **Weights ($w_{ij}$)**: A scalar associated with each control point $P_{ij}$. A higher weight "pulls" the surface closer to that control point.
*   **Basis Functions ($N_{i,p}$)**: Piecewise polynomial functions defined over a knot vector.
*   **Rational Surface**: The term "rational" refers to the use of weights and a division step, allowing for the exact representation of conic sections (circles, ellipses).

## 3. Theory
A point on a NURBS surface $S(u, v)$ is defined as:
$$S(u, v) = \frac{\sum_{i=0}^n \sum_{j=0}^m N_{i,p}(u) N_{j,q}(v) w_{i,j} P_{i,j}}{\sum_{i=0}^n \sum_{j=0}^m N_{i,p}(u) N_{j,q}(v) w_{i,j}}$$
where $P_{i,j}$ are the control points, $w_{i,j}$ are weights, and $N_{i,p}, N_{j,q}$ are the B-spline basis functions of degrees $p$ and $q$.

The calculation typically follows these steps:
1.  **Locate Knots**: Find the indices of the knots $u$ and $v$ in their respective knot vectors.
2.  **Evaluate Basis Functions**: Compute the values of all non-zero basis functions at $u$ and $v$ using the **Cox-de Boor recursion formula**.
3.  **Summation**: Compute the weighted sum of the control points and the sum of the weights.
4.  **Division**: Divide the weighted point sum by the total weight to find the final 3D point.

## 4. Pseudo code
```python
function EvaluateNURBSSurface(control_points, weights, knots_u, knots_v, p, q, u, v):
    # 1. Find knot spans
    span_u = FindKnotSpan(n, p, u, knots_u)
    span_v = FindKnotSpan(m, q, v, knots_v)
    
    # 2. Evaluate basis functions
    Nu = BasisFunctions(span_u, u, p, knots_u)
    Nv = BasisFunctions(span_v, v, q, knots_v)
    
    # 3. Form weighted point sum
    sum_w_p = Vector3(0, 0, 0)
    sum_w = 0
    
    for l in range(q + 1):
        temp = Vector3(0, 0, 0)
        temp_w = 0
        for k in range(p + 1):
            idx_u = span_u - p + k
            idx_v = span_v - q + l
            
            w = weights[idx_u][idx_v]
            p_val = control_points[idx_u][idx_v]
            
            sum_w_p += Nu[k] * Nv[l] * w * p_val
            sum_w += Nu[k] * Nv[l] * w
            
    # 4. Final perspective division
    return sum_w_p / sum_w
```

## 5. Parameters Selections
*   **Degree ($p, q$)**: Usually $p=3, q=3$ (bicubic) for smooth modeling.
*   **Knot Vector Type**: **Clamped** knot vectors (where the first and last $p+1$ knots are identical) ensure the surface passes exactly through its corner control points.

## 6. Complexity
*   **Time Complexity**: $O(p^2 + q^2)$ to evaluate the basis functions, plus $O(p \cdot q)$ for the final summation. This is extremely efficient for low degrees.
*   **Space Complexity**: $O(n \cdot m)$ to store the control point and weight grids.

## 7. Usages
*   **Industrial CAD**: Standard data format (IGES, STEP) for exchanging 3D models between different engineering software (SolidWorks, Rhino, CATIA).
*   **Reverse Engineering**: Fitting smooth surfaces to scanned point cloud data.
*   **Scientific Visualization**: Smoothly interpolating scattered spatial data (e.g., bathymetry or atmospheric pressure).
*   **High-End Animation**: Rendering complex character models (Pixar's RenderMan uses NURBS extensively).
*   **Naval Architecture**: Designing boat hulls for optimal fluid flow.

## 8. Testing methods and Edge cases
*   **Analytic Shapes**: Verify that a NURBS surface with appropriate weights can exactly represent a sphere or a cylinder.
*   **Weights of 1**: If all weights are 1.0, the surface must behave identically to a non-rational B-spline surface.
*   **Boundary Conditions**: Verify that the surface interpolates its corner control points (for clamped knots).
*   **Numerical Stability**: Ensure the denominator (total weight) does not approach zero.
*   **Derivative Calculation**: Verify that the surface normals (calculated from $u$ and $v$ derivatives) are smooth and consistent.

## 9. References
*   Piegl, L., & Tiller, W. (1997). "The NURBS Book". Springer.
*   Rogers, D. F. (2001). "An Introduction to NURBS: With Historical Perspective". Morgan Kaufmann.
*   Farin, G. (2002). "Curves and Surfaces for CAGD: A Practical Guide". Morgan Kaufmann.
*   Wikipedia: [Non-uniform rational B-spline](https://en.wikipedia.org/wiki/Non-uniform_rational_B-spline)
