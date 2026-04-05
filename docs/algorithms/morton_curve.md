# Morton Curve (Z-Order)

## 1. Overview
The Morton curve (also known as Z-order) is a space-filling curve that maps multidimensional data to one dimension while maintaining some level of spatial locality. It is much simpler to implement than the Hilbert curve, as it is based on **bit-interleaving** of coordinates. The resulting path forms a "Z" shape at each scale, which is why it is commonly called Z-order. It is a fundamental technique for spatial indexing in computer graphics and databases.

## 2. Definitions
*   **Bit-Interleaving**: Creating a single number by alternating bits from two or more source numbers.
*   **Z-Order Index**: The 1D index (Morton code) resulting from bit-interleaving.
*   **Locality**: The property where points close in space are also close on the 1D curve. Z-order preserves locality well, but not as consistently as the Hilbert curve.

## 3. Theory
For 2D coordinates $(x, y)$, the Morton code is computed by taking the binary representation of $x$ and $y$ and interleaving them:
*   $x = (x_n x_{n-1} \dots x_1 x_0)_2$
*   $y = (y_n y_{n-1} \dots y_1 y_0)_2$
*   $Z = (y_n x_n y_{n-1} x_{n-1} \dots y_0 x_0)_2$

This process is extremely fast because it can be implemented with simple bitwise shifts and masks. Geometrically, this recursively partitions the space into four quadrants, ordering them in a Z-pattern: (0,0) $\to$ (1,0) $\to$ (0,1) $\to$ (1,1).

## 4. Pseudo code
```python
function XYtoMorton(x, y):
    morton_code = 0
    # Process bits one by one
    for i in range(MAX_BITS):
        # Extract i-th bit from x and y
        bit_x = (x >> i) & 1
        bit_y = (y >> i) & 1
        
        # Interleave bits: y_i at position 2*i + 1, x_i at position 2*i
        morton_code |= (bit_x << (2 * i))
        morton_code |= (bit_y << (2 * i + 1))
        
    return morton_code

# Faster version using bit manipulation magic (for 16-bit x, y)
function InterleaveBits(x):
    x = (x | (x << 8)) & 0x00FF00FF
    x = (x | (x << 4)) & 0x0F0F0F0F
    x = (x | (x << 2)) & 0x33333333
    x = (x | (x << 1)) & 0x55555555
    return x
```

## 5. Parameters Selections
*   **Bit Depth**: The number of bits used for each coordinate (e.g., 16 bits for a $2^{16} \times 2^{16}$ grid).
*   **Interleaving Order**: Conventionally $y$ bits are placed in higher positions, but $x$-first is also used.

## 6. Complexity
*   **Transformation**: $O(1)$ for fixed-size integers using bit manipulation (or $O(n)$ where $n$ is bits).
*   **Space**: $O(1)$ auxiliary space.

## 7. Usages
*   **Quadtrees/Octrees**: Morton codes can be used to uniquely represent nodes in a linear quadtree/octree, making them extremely fast to navigate.
*   **Texture Mapping**: Storing textures in Morton order (often called "swizzling") significantly improves GPU texture cache hit rates by ensuring local pixels are stored close together in memory.
*   **Spatial Databases**: Efficient range queries and nearest neighbor searches.
*   **Video Compression**: Partitioning macroblocks in a locality-preserving order.
*   **GPGPU Optimization**: Ordering parallel threads to match memory access patterns.

## 8. Testing methods and Edge cases
*   **Invertibility**: Ensure bit-interleaving can be reversed (de-interleaving) to recover the original $(x, y)$.
*   **Boundary Points**: Test the mapping at $(0,0)$ and the maximum possible coordinate (e.g., $(2^{16}-1, 2^{16}-1)$).
*   **Adjacency**: Note that Z-order has "jumps" where sequential points on the curve are geographically distant. Verify that these occur only at specific power-of-two boundaries.
*   **High Dimensions**: Test that the code works correctly for 3D $(x, y, z)$ coordinates.

## 9. References
*   Morton, G. M. (1966). "A computer-oriented geodetic data base and a new technique in file sequencing". IBM Technical Report.
*   Samet, H. (1984). "The Quadtree and Related Hierarchical Data Structures". ACM Computing Surveys.
*   Wikipedia: [Z-order curve](https://en.wikipedia.org/wiki/Z-order_curve)
