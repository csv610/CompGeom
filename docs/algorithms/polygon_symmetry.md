# Polygon Symmetry Detection

## 1. Overview
Polygon symmetry detection is the problem of identifying whether a given polygon possesses symmetries such as rotational symmetry or reflectional (axial) symmetry. A polygon is symmetric if it looks identical after a specific geometric transformation. Detecting these symmetries is a classic problem in computational geometry with applications in computer vision, robotics, and geometric design.

## 2. Definitions
*   **Reflectional Symmetry (Axial Symmetry)**: A polygon has axial symmetry if there exists a line (the axis of symmetry) such that reflecting the polygon across this line leaves it unchanged.
*   **Rotational Symmetry**: A polygon has rotational symmetry of order $k > 1$ if rotating it by $360^\circ/k$ around its centroid leaves it unchanged.
*   **Centroid**: The average position of all the points in the polygon, which must be the fixed point for any rotational symmetry.

## 3. Theory
The most efficient algorithm for detecting polygon symmetry is based on **string matching**, similar to the polygon congruence algorithm.
1.  Represent the polygon as a sequence of (angle, edge-length) pairs: $S = (a_1, l_1, a_2, l_2, \dots, a_n, l_n)$.
2.  **Rotational Symmetry**: Find all cyclic shifts of $S$ that are identical to $S$ itself. This can be done using the **Knuth-Morris-Pratt (KMP)** algorithm by searching for $S$ in $S+S$ (excluding the trivial match at position 0).
3.  **Reflectional Symmetry**: Check if the sequence $S$ is a cyclic shift of its own reverse sequence $S^R$. If it is, the axes of symmetry must pass through either a vertex or the midpoint of an edge.

## 4. Pseudo code
```python
function DetectSymmetries(polygon):
    sig = GenerateSignature(polygon)
    n = len(polygon)
    
    # 1. Detect Rotational Symmetry
    # Find all occurrences of sig in sig + sig
    rotations = KMP_AllMatches(sig + sig[:-1], sig)
    order_k = len(rotations)
    
    # 2. Detect Reflectional Symmetry
    sig_rev = ReverseSignature(sig)
    reflection_matches = KMP_AllMatches(sig + sig, sig_rev)
    
    axes = []
    for match_pos in reflection_matches:
        # Calculate the axis line based on match position
        axis = CalculateAxis(match_pos, polygon)
        axes.append(axis)
        
    return order_k, axes

function GenerateSignature(polygon):
    # Returns (alpha_1, d_1, alpha_2, l_2, ...)
    # where alpha is interior angle and d is edge length
    pass
```

## 5. Parameters Selections
*   **Precision (Epsilon)**: Symmetry detection is highly sensitive to noise. A tolerance should be used when comparing angles and lengths.
*   **Signature Choice**: Using interior angles and edge lengths makes the detection invariant to translation, rotation, and scaling.

## 6. Complexity
*   **Signature Generation**: $O(n)$.
*   **Rotational Check**: $O(n)$ using KMP.
*   **Reflectional Check**: $O(n)$ using KMP on the reversed sequence.
*   **Total Time**: $O(n)$ for a polygon with $n$ vertices.

## 7. Usages
*   **Computer Vision**: Recognizing symmetric objects (like tools, symbols, or parts) in images regardless of their orientation.
*   **Robotics**: Planning grasps for symmetric objects (where multiple orientations are equivalent).
*   **Geometric Design (CAD)**: Enforcing symmetry constraints during modeling.
*   **Chemistry**: Identifying the point group symmetry of molecular structures represented as polygons or polyhedra.
*   **Art and Architecture**: Analyzing and generating symmetric patterns and tilings.

## 8. Testing methods and Edge cases
*   **Regular Polygons**: A regular $n$-gon should have rotational symmetry of order $n$ and $n$ axes of reflectional symmetry.
*   **Isosceles Triangle**: Should have one axis of symmetry and no rotational symmetry ($k=1$).
*   **Rectangle**: Should have rotational symmetry of order 2 and two axes of symmetry.
*   **Parallelogram**: Should have rotational symmetry of order 2 but no axes of symmetry (in general).
*   **No Symmetry**: Test on random, scalene polygons to ensure they return order 1 and zero axes.
*   **Precision Issues**: Test with nearly symmetric polygons to verify the epsilon handling.

## 9. References
*   Atallah, M. J. (1985). "On symmetry detection". IEEE Transactions on Computers.
*   Highnam, P. T. (1986). "Optimal algorithms for finding the symmetries of a planar point set". Information Processing Letters.
*   Wolter, J. D., Woo, T. C., & Volz, R. A. (1985). "Optimal algorithms for detecting relevant symmetries in polygons". IEEE Transactions on Robotics and Automation.
*   Wikipedia: [Symmetry in geometry](https://en.wikipedia.org/wiki/Symmetry_in_geometry)
