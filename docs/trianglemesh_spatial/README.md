# `trianglemesh/spatial.py`

Purpose: spatial indexing data structures for 2D points.

Algorithms and structures:
- point quadtree with recursive quadrant insertion
- KD-tree with alternating-axis median splits

Inputs: lists of `Point` objects or streamed point insertions.

Outputs: tree nodes or textual displays for the CLI wrappers.

Assumptions: in-memory educational implementations, not optimized production indexes.
