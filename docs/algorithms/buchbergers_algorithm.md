# Buchberger's Algorithm (Gröbner Bases)

## 1. Overview
Buchberger's algorithm is a fundamental method in computational algebraic geometry for computing a **Gröbner basis** of a polynomial ideal. Much like the Gaussian elimination algorithm for linear systems, Buchberger's algorithm transforms a set of multivariate polynomials into a "standard" form that makes it easy to solve systems of equations, perform polynomial division, and analyze the properties of the underlying algebraic variety.

## 2. Definitions
*   **Polynomial Ideal ($I$)**: The set of all linear combinations of a given set of generators $\{f_1, \dots, f_m\}$ with polynomial coefficients.
*   **Monomial Order**: A systematic way of deciding which term in a polynomial is the "leading" term (e.g., Lexicographical or Graded Lex).
*   **Gröbner Basis**: A specific set of generators for an ideal such that the leading term of any polynomial in the ideal is divisible by the leading term of one of the generators.
*   **S-Polynomial**: A polynomial constructed from two polynomials to cancel their leading terms, used to check if the current basis is "complete."

## 3. Theory
The algorithm starts with an initial set of generators $G$. It systematically checks all pairs of polynomials $(f, g)$ in $G$ and calculates their **S-polynomial**:
$$S(f, g) = \frac{L}{LT(f)} f - \frac{L}{LT(g)} g$$
where $L = \text{lcm}(LM(f), LM(g))$. 

The S-polynomial is then reduced by the current basis $G$ using multivariate polynomial division. If the remainder is non-zero, it means $G$ is not yet a Gröbner basis, and the remainder is added to $G$. This process continues until the S-polynomial of every pair in $G$ reduces to zero.

## 4. Pseudo code
```python
function Buchberger(F, monomial_order):
    G = F
    pairs = {(f_i, f_j) for f_i, f_j in G if i < j}
    
    while pairs:
        f, g = pairs.pop()
        
        # 1. Form S-polynomial
        S = S_Polynomial(f, g, monomial_order)
        
        # 2. Reduce S by the current basis G
        remainder = MultivariateDivision(S, G, monomial_order)
        
        # 3. If remainder is non-zero, it adds a new constraint
        if remainder != 0:
            for existing_g in G:
                pairs.add((existing_g, remainder))
            G.append(remainder)
            
    return G
```

## 5. Parameters Selections
*   **Monomial Order**: **Lexicographical** (Lex) is used for solving systems of equations, while **Graded Reverse Lexicographical** (Greverlex) is generally much faster for computing the basis.
*   **Selection Heuristic**: Choosing pairs with the smallest LCM of leading terms can improve performance.

## 6. Complexity
*   **Time Complexity**: In the worst case, the algorithm's complexity can be **doubly exponential** in the number of variables. However, for many practical problems, it is much faster.
*   **Space Complexity**: Can also grow extremely large as many intermediate polynomials are generated.

## 7. Usages
*   **Solving Polynomial Systems**: Transforming a complex system into a Lex-ordered Gröbner basis (which looks like a "triangular" system) and solving by back-substitution.
*   **Surface Implicitization**: Converting a parametric surface (e.g., Bézier or NURBS) into an implicit equation $f(x, y, z) = 0$.
*   **Collision Detection**: Determining if two curved surfaces (defined by algebraic equations) intersect.
*   **Robot Kinematics**: Solving the inverse kinematics problem for robot arms with multiple joints.
*   **Motion Planning**: Checking for intersections between objects in configuration space.

## 8. Testing methods and Edge cases
*   **Linear Systems**: On a system of linear equations, Buchberger should perform identically to Gaussian elimination.
*   **Single Variable**: On polynomials in $x$, it should behave like the Euclidean algorithm for finding the GCD.
*   **Inconsistent Systems**: If the system has no solution, the Gröbner basis should contain the constant 1.
*   **Redundant Generators**: The algorithm should eliminate redundant polynomials.
*   **Monomial Order Sensitivity**: Verify that the resulting basis is correct for different orders (Lex vs. Degrevlex).

## 9. References
*   Buchberger, B. (1965). "An Algorithm for Finding the Basis Elements of the Residue Class Ring of a Zero Dimensional Polynomial Ideal". PhD Thesis.
*   Cox, D., Little, J., & O'Shea, D. (2007). "Ideals, Varieties, and Algorithms". Springer.
*   Wikipedia: [Buchberger's algorithm](https://en.wikipedia.org/wiki/Buchberger%27s_algorithm)
