# Polygon Matching (Congruence and Similarity)

## 1. Overview
Polygon matching is the problem of determining whether two given polygons $P$ and $Q$ are identical under a set of transformations (congruence) or whether one is a scaled version of the other (similarity). This is a specialized form of shape matching that focuses on the exact geometric properties of the boundary. It is essential for pattern recognition, computer vision, and verifying geometric designs.

## 2. Definitions
*   **Congruence**: Two polygons are congruent if they have the same shape and size. They can be mapped to each other via translation, rotation, and reflection.
*   **Similarity**: Two polygons are similar if they have the same shape but possibly different sizes. They can be mapped via congruence plus scaling.
*   **Geometric Signature**: A sequence of values (like edge lengths and angles) that uniquely describes a polygon's shape and is invariant under certain transformations.

## 3. Theory
The most robust way to check for polygon matching is to construct a **string representation** of the polygon and use string-matching algorithms.
1.  For each vertex, calculate its **internal angle** and the **length of the edge** following it.
2.  Form a sequence: $(a_1, l_1, a_2, l_2, \dots, a_n, l_n)$.
3.  To handle rotation, treat the sequence as a circular string.
4.  Two polygons are congruent if their sequences are cyclic shifts of each other.
5.  Two polygons are similar if their angle sequences are identical and their edge length sequences are proportional.

The **Knuth-Morris-Pratt (KMP)** algorithm can be used to find cyclic shifts in linear time by searching for sequence $S$ in $S+S$.

## 4. Pseudo code
```python
function IsCongruent(P, Q):
    if len(P) != len(Q): return False
    
    # 1. Generate signatures
    sigP = GenerateSignature(P)
    sigQ = GenerateSignature(Q)
    
    # 2. Handle reflection (optional)
    if IsCyclicShift(sigP, sigQ): return True
    if IsCyclicShift(sigP, Reverse(sigQ)): return True
    
    return False

function GenerateSignature(polygon):
    sig = []
    n = len(polygon)
    for i in range(n):
        p1 = polygon[i-1]
        p2 = polygon[i]
        p3 = polygon[(i+1)%n]
        
        angle = CalculateAngle(p1, p2, p3)
        length = Distance(p2, p3)
        sig.append((angle, length))
    return sig

function IsCyclicShift(S1, S2):
    # KMP search for S2 in S1 + S1
    return KMP_Search(S1 + S1, S2)
```

## 5. Parameters Selections
*   **Precision**: Matching should use a small epsilon for floating-point comparisons of angles and lengths.
*   **Transformations**: Decide if reflection is allowed (mirror symmetry).
*   **Normalization**: For similarity matching, divide all edge lengths by the total perimeter or the longest edge.

## 6. Complexity
*   **Signature Generation**: $O(n)$.
*   **Matching**: $O(n)$ using KMP for cyclic shifts.
*   **Total Time**: $O(n)$.
*   **Space Complexity**: $O(n)$ to store the signatures.

## 7. Usages
*   **Computer Vision**: Identifying an object in an image by matching its contour to a template.
*   **CAD/CAM**: Finding duplicate parts in a complex mechanical assembly.
*   **Architecture**: Identifying repeating patterns or tiles in a floor plan.
*   **Geographic Information Systems (GIS)**: Matching building footprints across different map revisions.
*   **Character Recognition**: Matching the strokes of a drawn letter to a font database.

## 8. Testing methods and Edge cases
*   **Rotated Polygons**: Verify that a polygon matches its rotated version.
*   **Mirrored Polygons**: Test if the algorithm correctly identifies reflections.
*   **Regular Polygons**: A regular $n$-gon should have $n$ different valid cyclic shifts.
*   **Degenerate Polygons**: Test on triangles or polygons with collinear vertices.
*   **Self-Intersecting Polygons**: Ensure the signature is robust for non-simple polygons.
*   **Numerical Sensitivity**: Test with polygons having very small edges or angles.

## 9. References
*   Arkin, E. M., Chew, L. P., Huttenlocher, D. P., Kedem, K., & Mitchell, J. S. (1991). "An efficiently computable metric for comparing polygonal shapes". IEEE Transactions on Pattern Analysis and Machine Intelligence.
*   Manber, U. (1989). "Introduction to Algorithms: A Creative Approach". Addison-Wesley.
*   Wikipedia: [Congruence (geometry)](https://en.wikipedia.org/wiki/Congruence_(geometry))
