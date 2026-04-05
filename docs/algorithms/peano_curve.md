# Peano Curve

## 1. Overview
The Peano curve is the first known example of a space-filling curve, discovered by Giuseppe Peano in 1890. It is a continuous mapping from a 1D unit interval to a 2D unit square. Unlike the Hilbert curve, which is based on a $2 \times 2$ subdivision, the Peano curve is based on a $3 \times 3$ subdivision. It is an important foundational structure in mathematical analysis and fractal geometry.

## 2. Definitions
*   **Space-Filling Curve**: A continuous function whose image contains the entire 2D region.
*   **Order (n)**: The number of recursive subdivisions. An order-$n$ Peano curve covers a grid of $3^n \times 3^n$ cells.
*   **Locality**: The property of mapping nearby 1D points to nearby 2D points.

## 3. Theory
The Peano curve is constructed recursively using a $3 \times 3$ grid. 
1.  For order $n=1$, the space is divided into 9 squares.
2.  The curve visits these squares in an S-like pattern, ensuring that it enters and exits each square in a way that allows for continuous connection between neighbors.
3.  Each of the 9 squares is then recursively replaced by a smaller $3 \times 3$ Peano curve. Some of these sub-curves must be reflected or rotated to maintain the overall continuity.

Mathematically, the Peano curve is defined by a base-3 representation of coordinates. Interleaving these base-3 digits (trits) provides the 1D index, though the digits must be flipped for certain sub-quadrants to preserve the curve's continuity.

## 4. Pseudo code
```python
function PeanoIndex(n, x, y):
    # Mapping coordinates (x, y) to a 1D index
    # Based on base-3 representation
    idx = 0
    for i in range(n-1, -1, -1):
        trit_x = (x // (3**i)) % 3
        trit_y = (y // (3**i)) % 3
        
        # Handle reflections for even-numbered segments
        if x_is_reversed:
            trit_x = 2 - trit_x
        if y_is_reversed:
            trit_y = 2 - trit_y
            
        # Segment index (0-8)
        segment = trit_y * 3 + trit_x
        idx = idx * 9 + segment
        
        # Update reflection state for next level
        UpdateReflectionState(trit_x, trit_y)
        
    return idx
```

## 5. Parameters Selections
*   **Order ($n$ )**: Determines the resolution of the grid ($3^n \times 3^n$).
*   **Grid Size**: Must be a power of 3.

## 6. Complexity
*   **Transformation**: $O(n)$ base-3 digit operations.
*   **Space**: $O(1)$ auxiliary space.

## 7. Usages
*   **Theoretical Analysis**: A fundamental counter-example in topology and real analysis (showing a continuous mapping from 1D to 2D).
*   **Image Processing**: Scanning images in a way that respects local structures, similar to Hilbert scans.
*   **Data Organization**: Multidimensional indexing (though base-2 curves like Hilbert and Morton are much more common in digital hardware).
*   **Fractal Design**: Used in generative art and architectural patterns.

## 8. Testing methods and Edge cases
*   **Continuity**: Verify that for any index $i$, the Euclidean distance between `Peano(i)` and `Peano(i+1)` is exactly 1 unit in the grid.
*   **Full Coverage**: Verify that every $(x, y)$ coordinate in a $3^n \times 3^n$ grid is mapped to a unique index $0 \dots 9^n - 1$.
*   **Boundary Cases**: Test coordinates $(0,0)$ and the maximum coordinate $(3^n-1, 3^n-1)$.
*   **Reflections**: Carefully test the "flipping" logic in the S-pattern to ensure the curve doesn't have breaks.

## 9. References
*   Peano, G. (1890). "Sur une courbe, qui remplit toute une aire plaine". Mathematische Annalen.
*   Sagan, H. (1994). "Space-Filling Curves". Universitext.
*   Wikipedia: [Peano curve](https://en.wikipedia.org/wiki/Peano_curve)
