# Lower Envelopes

## 1. Overview
The lower envelope of a set of functions $f_1, f_2, \dots, f_n$ is the pointwise minimum of those functions: $L(x) = \min_i f_i(x)$. In computational geometry, the lower envelope is a fundamental structure used to solve problems related to visibility, optimization, and arrangements. For example, the lower envelope of a set of lines forms the boundary of their intersection (a convex polygon in the dual plane).

## 2. Definitions
*   **Lower Envelope**: The boundary formed by the pointwise minimum of a collection of functions.
*   **Upper Envelope**: The pointwise maximum of a collection of functions.
*   **Minimization Diagram**: The partition of the domain into regions where a specific function $f_i$ is the minimum.
*   **Complexity**: The number of segments (or patches in higher dimensions) that form the lower envelope.

## 3. Theory
The complexity of the lower envelope depends on how many times any two functions can intersect.
1.  **Lines**: Any two lines intersect at most once. The lower envelope of $n$ lines is a convex chain with at most $n$ segments.
2.  **Line Segments**: Two segments can intersect at most once, but the envelope can have up to $O(n \alpha(n))$ segments due to the "visibility" of segments behind each other.
3.  **Parabolas/Circles**: Two functions intersect at most twice. The envelope complexity is $O(n)$.
4.  **General Curves**: If any two curves intersect at most $s$ times, the complexity is bounded by the Davenport-Schinzel sequence $\lambda_s(n)$.

The lower envelope can be computed using a **Divide and Conquer** algorithm:
1.  Divide the set of functions into two halves.
2.  Recursively compute the lower envelope of each half.
3.  Merge the two envelopes by finding their intersection points and keeping the lower segments.

## 4. Pseudo code
```python
function ComputeLowerEnvelope(functions, x_min, x_max):
    if len(functions) == 1:
        return [(functions[0], x_min, x_max)]
        
    # 1. Split
    mid = len(functions) // 2
    left_env = ComputeLowerEnvelope(functions[:mid], x_min, x_max)
    right_env = ComputeLowerEnvelope(functions[mid:], x_min, x_max)
    
    # 2. Merge
    merged = []
    # Intersect the two piecewise-defined envelopes
    # left_env: [(f1, x1, x2), (f2, x2, x3), ...]
    # right_env: [(g1, x1, y2), (g2, y2, y3), ...]
    for segment_L in left_env:
        for segment_R in right_env:
            # Find interval where both segments exist
            common_start = max(segment_L.start, segment_R.start)
            common_end = min(segment_L.end, segment_R.end)
            
            if common_start < common_end:
                # Find intersections of f_L and f_R in this interval
                intersections = FindIntersections(segment_L.f, segment_R.f, 
                                                  common_start, common_end)
                # Split interval at intersections and pick the lower function
                merged.extend(PickLower(segment_L.f, segment_R.f, 
                                        common_start, common_end, intersections))
                
    return Simplify(merged)
```

## 5. Parameters Selections
*   **Function Type**: Linear, polynomial, or arbitrary continuous functions.
*   **Intersection Solver**: A robust numerical or symbolic solver is needed to find where $f_i(x) = f_j(x)$.

## 6. Complexity
*   **Complexity of Envelope**: $O(\lambda_s(n))$ where $s$ is the number of intersections.
*   **Construction Time**: $O(\lambda_s(n) \log n)$ using divide and conquer.
*   **Space Complexity**: $O(\lambda_s(n))$ to store the resulting segments.

## 7. Usages
*   **Visibility**: Calculating the "horizon" of a set of mountains or the region visible from a point.
*   **Motion Planning**: Finding the safest path by maximizing the distance to the nearest obstacle (lower envelope of distance functions).
*   **Duality**: Solving problems like the "Width of a Point Set" or "Diameter" in the dual plane.
*   **Dynamic Programming**: Optimizing decisions over time where costs are modeled as functions.
*   **Statistics**: Calculating the "support" of a probability distribution.

## 8. Testing methods and Edge cases
*   **Non-Intersecting Functions**: The envelope should simply be the single function that is globally minimum.
*   **Vertical Functions**: Ensure the algorithm handles discontinuities or vertical lines.
*   **Touching Functions**: Verify that tangencies (where functions touch but don't cross) don't create unnecessary segments.
*   **Overlap**: Handle cases where two functions are identical over an interval.
*   **Large $n$**: Verify the near-linear growth of the result size.

## 9. References
*   Sharir, M., & Agarwal, P. K. (1995). "Davenport-Schinzel Sequences and Their Geometric Applications". Cambridge University Press.
*   Hershberger, J. (1989). "Finding the upper envelope of $n$ line segments in $O(n \log n)$ time". Information Processing Letters.
*   Edelsbrunner, H. (1987). "Algorithms in Combinatorial Geometry". Springer-Verlag.
*   Wikipedia: [Lower envelope](https://en.wikipedia.org/wiki/Lower_envelope)
