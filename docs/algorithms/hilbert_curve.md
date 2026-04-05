# Hilbert Curve

## 1. Overview
The Hilbert curve is a continuous fractal space-filling curve first described by David Hilbert in 1891. It is a mapping between 1D and 2D (or higher-dimensional) space that preserves locality: points that are close together on the 1D curve are also close together in the 2D plane. This property makes the Hilbert curve an invaluable tool for multidimensional indexing, data compression, and spatial analysis.

## 2. Definitions
*   **Space-Filling Curve**: A curve whose range contains the entire 2-dimensional unit square.
*   **Order (n)**: The number of recursive subdivisions. An order-$n$ Hilbert curve covers a grid of $2^n \times 2^n$ cells.
*   **Locality Preservation**: The property where distance on the curve (Hilbert index) correlates strongly with Euclidean distance in space.
*   **U-shape**: The basic motif of the Hilbert curve, which is rotated and reflected to form higher orders.

## 3. Theory
The Hilbert curve is constructed recursively. For order $n=1$, it is a simple U-shape connecting four cells. To create order $n+1$:
1.  The space is divided into four quadrants.
2.  Four order-$n$ curves are placed in the quadrants.
3.  The bottom-left curve is rotated $90^\circ$ clockwise.
4.  The bottom-right curve is rotated $90^\circ$ counter-clockwise and reflected.
5.  The four curves are connected by three segments.

The transformation from 2D coordinates $(x, y)$ to a 1D index $d$ (and vice versa) involves bitwise operations and coordinate rotations. As the order $n \to \infty$, the curve fills the entire square.

## 4. Pseudo code
```python
function XYtoHilbert(n, x, y):
    d = 0
    s = 2**(n - 1)
    while s > 0:
        rx = (x & s) > 0
        ry = (y & s) > 0
        d += s * s * ((3 * rx) ^ ry)
        # Rotate and flip
        x, y = RotateHilbert(s, x, y, rx, ry)
        s //= 2
    return d

function RotateHilbert(n, x, y, rx, ry):
    if ry == 0:
        if rx == 1:
            x = n - 1 - x
            y = n - 1 - y
        return y, x
    return x, y
```

## 5. Parameters Selections
*   **Order ($n$ )**: Typically chosen so that $2^n$ matches the resolution of the spatial grid.
*   **Dimension**: While most common in 2D, the Hilbert curve can be extended to any number of dimensions $k$.

## 6. Complexity
*   **Transformation**: $O(n)$ bitwise operations for an order-$n$ curve. For a fixed grid size, this is essentially $O(1)$.
*   **Space**: $O(1)$ auxiliary space to perform the coordinate mapping.

## 7. Usages
*   **Spatial Indexing**: Organizing data in databases (like MongoDB or GeoJSON) for faster range queries.
*   **Image Dithering**: Ordering pixels for error diffusion to minimize visual artifacts.
*   **Parallel Computing**: Mapping multidimensional tasks to linear processing units while maintaining local data relationships (e.g., in domain decomposition).
*   **Data Compression**: Improving the performance of compression algorithms by clustering similar nearby values.
*   **Cache Optimization**: Storing 2D arrays in Hilbert order to improve the L1/L2 cache hit rate for local access patterns.

## 8. Testing methods and Edge cases
*   **Invertibility**: Verify that `HilbertToXY(XYtoHilbert(x, y)) == (x, y)` for all points in a grid.
*   **Adjacency**: Verify that points with sequential indices $d, d+1$ are always Manhattan neighbors in the 2D grid.
*   **Large Order**: Test the transformation with $n=31$ to ensure bitwise operations don't overflow 64-bit integers.
*   **All Quadrants**: Test points in each of the four main quadrants to ensure rotation and reflection logic is correct.

## 9. References
*   Hilbert, D. (1891). "Über die stetige Abbildung einer Linie auf ein Flächenstück". Mathematische Annalen.
*   Sagan, H. (1994). "Space-Filling Curves". Universitext.
*   Moon, B., Jagadish, H. V., Faloutsos, C., & Saltz, J. H. (2001). "Analysis of the Clustering Properties of the Hilbert Space-Filling Curve". IEEE Transactions on Knowledge and Data Engineering.
*   Wikipedia: [Hilbert curve](https://en.wikipedia.org/wiki/Hilbert_curve)
