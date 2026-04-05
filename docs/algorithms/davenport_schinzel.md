# Davenport-Schinzel Sequences

## 1. Overview
A Davenport-Schinzel sequence is a sequence of symbols that satisfies specific constraints on the alternating sub-sequences it can contain. These sequences provide a powerful combinatorial framework for analyzing the complexity of the **lower envelope** of a set of functions. In computational geometry, they are used to bound the complexity of arrangements of curves, motion planning visibility, and dynamic geometric structures.

## 2. Definitions
*   **DS Sequence of order s**: A sequence $U = (u_1, u_2, \dots, u_m)$ over an alphabet of $n$ symbols such that:
    1.  No two adjacent symbols are the same ($u_i \ne u_{i+1}$).
    2.  It does not contain any alternating sub-sequence of length $s+2$ of the form $a, b, a, b, \dots$.
*   **$\lambda_s(n)$**: The maximum possible length of a Davenport-Schinzel sequence of order $s$ on $n$ symbols.
*   **Lower Envelope**: The pointwise minimum of a collection of functions.

## 3. Theory
The importance of DS sequences stems from their relationship to function intersections. If we have $n$ continuous functions such that any two functions intersect at most $s$ times, then the sequence of function indices that form the **lower envelope** is a Davenport-Schinzel sequence of order $s$.

For example:
*   **Order $s=1$**: Functions intersect at most once (e.g., lines). $\lambda_1(n) = n$.
*   **Order $s=2$**: Functions intersect at most twice (e.g., parabolas). $\lambda_2(n) = 2n - 1$.
*   **Order $s=3$**: Functions intersect at most three times. $\lambda_3(n) = \Theta(n \alpha(n))$, where $\alpha(n)$ is the extremely slow-growing inverse Ackermann function.

This theory allows us to prove that the complexity of the lower envelope of $n$ line segments is $O(n \alpha(n))$, which is much smaller than the total number of intersections $O(n^2)$.

## 4. Pseudo code
### Computing the Lower Envelope (Recursive)
```python
function LowerEnvelope(functions, start, end):
    if len(functions) == 1:
        return functions[0]
        
    # 1. Divide functions into two sets
    mid = len(functions) // 2
    left_env = LowerEnvelope(functions[:mid], start, end)
    right_env = LowerEnvelope(functions[mid:], start, end)
    
    # 2. Merge the two envelopes
    # This involves finding the intersection points of the two envelopes
    merged_env = MergeEnvelopes(left_env, right_env)
    
    return merged_env

function MergeEnvelopes(E1, E2):
    # E1 and E2 are sequences of (function_id, interval)
    # Find all points where f_E1(x) == f_E2(x)
    intersections = FindIntersections(E1, E2)
    # Re-partition the interval based on which function is lower
    return ResultingSequence(E1, E2, intersections)
```

## 5. Parameters Selections
*   **Order ($s$ )**: Depends on the type of geometric primitives (e.g., $s=1$ for lines, $s=2$ for circles, $s=3$ for line segments).
*   **Alphabet Size ($n$ )**: The number of geometric objects.

## 6. Complexity
*   **Maximum Length**: $\lambda_s(n)$ is near-linear for any fixed $s$. For example, $\lambda_3(n) = O(n \alpha(n))$.
*   **Construction Time**: The lower envelope can be computed in $O(\lambda_s(n) \log n)$ time using a divide-and-conquer approach.

## 7. Usages
*   **Arrangements**: Bounding the number of edges on a single cell or the lower envelope of an arrangement of curves.
*   **Motion Planning**: Analyzing the complexity of the "free space" for a robot moving among obstacles.
*   **Visibility**: Calculating the complexity of the region visible from a point in a dynamic environment.
*   **Kinetic Data Structures**: Tracking the minimum value among a set of moving points.
*   **Shortest Paths**: Computing the visibility graph of a set of segments.

## 8. Testing methods and Edge cases
*   **Non-Intersecting Functions**: The envelope should simply follow the lowest function for the entire range.
*   **Multiple Intersections**: Ensure the algorithm correctly captures all points where the lower envelope switches from one function to another.
*   **Touching vs. Crossing**: Handle cases where functions are tangent to each other without crossing.
*   **Vertical Segments**: Ensure the interval logic handles vertical discontinuities.
*   **Complexity Check**: Verify that the number of segments in the resulting envelope is within the DS bound $\lambda_s(n)$.

## 9. References
*   Davenport, H., & Schinzel, A. (1965). "A combinatorial problem connected with differential equations". American Journal of Mathematics.
*   Sharir, M., & Agarwal, P. K. (1995). "Davenport-Schinzel Sequences and Their Geometric Applications". Cambridge University Press.
*   Atallah, M. J. (1985). "Some dynamic computational geometry problems". Computers & Mathematics with Applications.
*   Wikipedia: [Davenport–Schinzel sequence](https://en.wikipedia.org/wiki/Davenport%E2%80%93Schinzel_sequence)
