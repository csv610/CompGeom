# `morton_walk2d.py`

Purpose: CLI for mapping Morton/Z-order indices to 2D coordinates.

Algorithm:
- interleaves/deinterleaves bits from the integer index
- reconstructs x and y coordinates bit by bit

Input: Morton index via command-line arguments.

Output: `(x, y)` coordinate.
