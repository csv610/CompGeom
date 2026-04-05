# Zigzag Curve (Snake Scan)

## 1. Overview
The zigzag curve (or snake scan) is a simple space-filling curve that visits every cell in a 2D grid in a back-and-forth pattern. Unlike Hilbert or Morton curves, it does not have fractal properties and is not designed for recursive locality preservation. Instead, it is highly efficient for sequential data access in rectangular arrays and is a common technique in image and video compression.

## 2. Definitions
*   **Zigzag Scan**: A path that traverses a grid row-by-row, alternating the direction of traversal for each row.
*   **Locality**: Sequential points on a zigzag curve are geographically close, but there are large jumps when moving between rows.
*   **Raster Scan**: A similar scan that always goes in the same direction (e.g., left-to-right). Zigzag is preferred in some cases because it maintains some horizontal locality at the row transitions.

## 3. Theory
The zigzag scan is constructed by iterating through the grid row by row.
*   For **even-indexed rows** (0, 2, ...), the curve moves from left to right.
*   For **odd-indexed rows** (1, 3, ...), the curve moves from right to left.

In image compression (like JPEG), a more specific **diagonal zigzag scan** is used. This scan traverses an $8 \times 8$ block of frequency coefficients in order of increasing frequency. This ensures that the low-frequency coefficients (which carry most of the image information) are grouped together, making them easier to compress.

## 4. Pseudo code
### Standard Snake Scan
```python
function SnakeScan(width, height):
    path = []
    for y in range(height):
        if y % 2 == 0:
            # Even row: left to right
            for x in range(width):
                path.append((x, y))
        else:
            # Odd row: right to left
            for x in range(width - 1, -1, -1):
                path.append((x, y))
    return path
```

### Diagonal Zigzag (JPEG style)
```python
function DiagonalZigzag(size):
    # Scan a square block diagonally
    path = []
    for s in range(2 * size - 1):
        if s % 2 == 0:
            # Up-right diagonal
            for y in range(size):
                x = s - y
                if 0 <= x < size:
                    path.append((x, y))
        else:
            # Down-left diagonal
            for x in range(size):
                y = s - x
                if 0 <= y < size:
                    path.append((x, y))
    return path
```

## 5. Parameters Selections
*   **Direction**: Can be row-major (standard snake) or diagonal (compression).
*   **Block Size**: For JPEG, the block size is fixed at $8 \times 8$.

## 6. Complexity
*   **Transformation**: $O(1)$ to compute a coordinate from an index (and vice versa) using modular arithmetic.
*   **Space**: $O(1)$ auxiliary space.

## 7. Usages
*   **Image/Video Compression (JPEG, MPEG)**: Ordering DCT coefficients to group low-frequency data, which improves the efficiency of run-length encoding (RLE).
*   **Display Technology**: Scanning pixels in CRT or LCD screens.
*   **Robotics/3D Printing**: Planning the path for a nozzle or sensor to cover a flat area (rasterizing a plane).
*   **Sensor Networks**: Ordering data collection from a grid of sensors.

## 8. Testing methods and Edge cases
*   **Full Coverage**: Verify that every $(x, y)$ in the grid appears exactly once in the scan.
*   **Continuity**: Verify that consecutive points in the path are Manhattan neighbors.
*   **Non-Square Grids**: Ensure the algorithm handles $W \ne H$ correctly.
*   **Zero/One dimensions**: Test on $1 \times N$ or $N \times 1$ grids.

## 9. References
*   Pennebaker, W. B., & Mitchell, J. L. (1992). "JPEG: Still Image Data Compression Standard". Van Nostrand Reinhold.
*   Wikipedia: [Zigzag](https://en.wikipedia.org/wiki/Zigzag)
