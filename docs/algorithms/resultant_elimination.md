# Resultant-based Elimination

## 1. Overview
Resultant-based elimination is a symbolic algebraic technique used to eliminate variables from a system of polynomial equations. The **resultant** of two polynomials is a scalar value (or another polynomial) that is zero if and only if the two original polynomials share a common root. By calculating the resultant with respect to one variable, we "project" the intersection of the two polynomials onto a lower-dimensional space. It is a faster alternative to Gröbner bases for many problems in surface implicitization and collision detection.

## 2. Definitions
*   **Resultant ($\text{Res}(f, g, x)$)**: A polynomial in the other variables that vanishes whenever $f$ and $g$ have a common solution for $x$.
*   **Sylvester Matrix**: A matrix formed from the coefficients of two polynomials $f$ and $g$. The determinant of this matrix is the resultant.
*   **Elimination**: The process of reducing a system of $n$ variables to a system of $n-1$ variables.
*   **Bezout Matrix**: A more compact matrix representation for computing the resultant of two polynomials of the same degree.

## 3. Theory
The resultant of two polynomials $f(x) = \sum a_i x^i$ and $g(x) = \sum b_j x^j$ is the determinant of the **Sylvester matrix**. 

For example, if $f(x, y)$ and $g(x, y)$ are two implicit curves, their resultant $\text{Res}_x(f, g)$ is a polynomial in $y$ whose roots are the $y$-coordinates of all intersection points. This allows us to solve for $y$ first and then back-substitute to find $x$.

For **Implicitization**, given parametric equations $x = X(t), y = Y(t), z = Z(t)$, we form the polynomials $f_1 = x - X(t), f_2 = y - Y(t), f_3 = z - Z(t)$ and calculate the resultant $\text{Res}_t(f_1, f_2, f_3)$ to eliminate the parameter $t$.

## 4. Pseudo code
```python
function Resultant(f, g, x):
    # f and g are polynomials in variable x
    
    # 1. Build Sylvester Matrix
    # Size (deg(f) + deg(g)) x (deg(f) + deg(g))
    S = BuildSylvesterMatrix(f, g, x)
    
    # 2. Compute Determinant
    # The determinant will be a polynomial in the other variables
    res = determinant(S)
    
    return res

function BuildSylvesterMatrix(f, g, x):
    # Rows are formed by shifting the coefficient vectors
    # [a_n, a_{n-1}, ..., a_0, 0, 0]
    # [0, a_n, a_{n-1}, ..., a_0, 0]
    # ...
    # [b_m, b_{m-1}, ..., b_0, 0, 0]
    # [0, b_m, b_{m-1}, ..., b_0, 0]
    return S
```

## 5. Parameters Selections
*   **Matrix Type**: Sylvester matrices are large and sparse. Bezout or Dixon matrices are much smaller for higher-order polynomials but are more complex to construct.
*   **Numerical Precision**: If coefficients are floating-point numbers, calculating the determinant can be numerically unstable. Using symbolic computation or arbitrary-precision arithmetic is recommended.

## 6. Complexity
*   **Time Complexity**: $O(d^3)$ where $d$ is the sum of the degrees of the two polynomials, based on the cost of the determinant calculation.
*   **Space Complexity**: $O(d^2)$ to store the Sylvester matrix.

## 7. Usages
*   **Surface Implicitization**: Converting parametric Bézier/NURBS surfaces into implicit $f(x, y, z) = 0$ equations for faster inside/outside tests.
*   **Curve/Surface Intersection**: Finding the exact points where a line (ray) intersects a curved surface.
*   **Collision Detection**: Determining if two curved objects intersect by checking if their resultant has any real roots.
*   **Robot Kinematics**: Solving inverse kinematics for complex linkages.
*   **Computer Aided Design (CAD)**: Boolean operations on curved surfaces.

## 8. Testing methods and Edge cases
*   **Two Lines**: The resultant of two linear equations $a_1 x + b_1$ and $a_2 x + b_2$ should be $a_1 b_2 - a_2 b_1$.
*   **Parallel Curves**: If curves never intersect, the resultant should be a non-zero constant.
*   **Coincident Curves**: If two curves are the same, the resultant will be identically zero.
*   **Leading Coefficient Zero**: Ensure the algorithm handles cases where the leading coefficient vanishes for certain values of the other variables.
*   **Large Degrees**: Verify that the determinant calculation remains robust for polynomials of degree 10+.

## 9. References
*   Sylvester, J. J. (1840). "A method of determining by inspection the form of the combined roots of two algebraic equations". Philosophical Magazine.
*   Cox, D., Little, J., & O'Shea, D. (2007). "Ideals, Varieties, and Algorithms". Springer.
*   Manocha, D. (1994). "Solving systems of polynomial equations using resultants". SIGGRAPH Course.
*   Wikipedia: [Resultant](https://en.wikipedia.org/wiki/Resultant)
