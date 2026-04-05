# Bézier Surface Evaluation

## 1. Overview
A Bézier surface is a smooth surface used in computer graphics and computer-aided design (CAD) that is controlled by a rectangular grid of points, called control points. It is a 2D extension of the Bézier curve. The surface is defined by a pair of parameters $(u, v)$, both in the range $[0, 1]$. Evaluating a Bézier surface means calculating the 3D coordinates $(x, y, z)$ corresponding to a given $(u, v)$ coordinate.

## 2. Definitions
*   **Control Points ($P_{ij}$)**: A grid of $m+1$ by $n+1$ points in 3D space that define the shape of the surface.
*   **Bernstein Polynomials ($B_{i,n}$)**: A set of polynomials used to weight the control points. 
*   **Tensor Product**: The method of forming the surface by multiplying two orthogonal Bézier curves.
*   **Degree ($m, n$)**: The polynomial degree in each of the two parametric directions.

## 3. Theory
A Bézier surface point $Q(u, v)$ is calculated using the formula:
$$Q(u, v) = \sum_{i=0}^m \sum_{j=0}^n B_{i,m}(u) B_{j,n}(v) P_{i,j}$$
The most efficient way to evaluate this is by using **de Casteljau's algorithm** in two steps:
1.  Evaluate $m+1$ separate Bézier curves in the $v$-direction using parameter $v$. This produces a temporary set of control points $P'_0, \dots, P'_m$ that depend only on $v$.
2.  Evaluate the single Bézier curve defined by $P'_i$ using parameter $u$. 

This "tensor product" approach effectively reduces the surface evaluation to several simpler curve evaluations.

## 4. Pseudo code
```python
function EvaluateBezierSurface(control_points, u, v):
    m = num_rows - 1
    n = num_cols - 1
    
    # 1. Reduce in the v direction
    # Evaluate m+1 curves of degree n
    temp_points = []
    for i in range(m + 1):
        # Extract i-th row of control points
        row = control_points[i]
        # Evaluate curve using de Casteljau
        p_prime = EvaluateBezierCurve(row, v)
        temp_points.append(p_prime)
        
    # 2. Reduce in the u direction
    # Evaluate 1 curve of degree m
    final_point = EvaluateBezierCurve(temp_points, u)
    
    return final_point

function EvaluateBezierCurve(points, t):
    # de Casteljau algorithm for a single parameter t
    current = points[:]
    while len(current) > 1:
        next_level = []
        for i in range(len(current) - 1):
            p = (1 - t) * current[i] + t * current[i+1]
            next_level.append(p)
        current = next_level
    return current[0]
```

## 5. Parameters Selections
*   **Parameter Range**: Parameters $u, v$ must be strictly within $[0, 1]$.
*   **Order**: The number of control points is $(m+1) \times (n+1)$. Typically $m=3, n=3$ for bicubic surfaces.

## 6. Complexity
*   **Time Complexity**: $O(m \cdot n^2 + m^2)$ using the two-step de Casteljau approach. For bicubic surfaces ($m=3, n=3$), this is a small constant.
*   **Space Complexity**: $O(m \cdot n)$ to store the control point grid.

## 7. Usages
*   **CAD (Computer Aided Design)**: Modeling car bodies, aircraft wings, and consumer products.
*   **Animation**: Smooth character skinning and facial deformations.
*   **TrueType/PostScript Fonts**: While fonts are 2D curves, they can be interpreted as 1D surfaces.
*   **Geometric Design**: Creating smooth transitions (blends) between different parts of a model.
*   **Fluid Simulation**: Representing the surface of a liquid with a set of smooth patches.

## 8. Testing methods and Edge cases
*   **Corners**: Verify that $Q(0,0), Q(0,1), Q(1,0), Q(1,1)$ exactly match the four corner control points.
*   **Flat Surface**: If all control points lie on a plane, the entire evaluated surface must lie on that plane.
*   **Degree Elevation**: Increasing the number of control points without changing the surface shape.
*   **Precision**: Ensure the surface remains smooth and doesn't "break" at $u, v \approx 0.5$.
*   **Continuity**: Checking that adjacent Bézier patches meet smoothly (G1 or C1 continuity).

## 9. References
*   Bézier, P. (1968). "How Renault Uses Numerical Control for Car Body Design and Tooling". SAE paper.
*   Farin, G. (2002). "Curves and Surfaces for CAGD: A Practical Guide". Morgan Kaufmann.
*   Piegl, L., & Tiller, W. (1997). "The NURBS Book". Springer.
*   Wikipedia: [Bézier surface](https://en.wikipedia.org/wiki/B%C3%A9zier_surface)
