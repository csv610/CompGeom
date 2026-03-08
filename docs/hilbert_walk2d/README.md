# `hilbert_walk2d.py`

Purpose: CLI for converting Hilbert curve indices to 2D grid coordinates.

Algorithm:
- uses `grid_walks.hilbert_index_to_coords`
- decodes Hilbert digits by iterative quadrant transforms

Input: index and order through command-line arguments.

Output: `(x, y)` coordinate on the Hilbert curve.
