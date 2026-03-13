# Spatial Index Structures

This package now includes several core data structures used in computational geometry:

- `build_kdtree(points)` builds a 2D KD-tree from `Point` objects.
- `range_search(root, min_x, max_x, min_y, max_y)` queries a KD-tree with an axis-aligned rectangle.
- `IntervalTree(intervals)` supports stabbing queries (`query_point`) and interval overlap queries (`query_interval`).
- `SegmentTree(values)` supports range aggregation with point updates.

## KD-Tree Range Search

Use the KD-tree when you need repeated orthogonal range queries over a static point set, such as selecting all sampled points inside a map window or view frustum slice.

```python
from compgeom import Point2D, build_kdtree, range_search

points = [
    Point2D(0, 0),
    Point2D(2, 1),
    Point2D(3, 4),
    Point2D(5, 2),
    Point2D(6, 5),
]

root = build_kdtree(points)
hits = range_search(root, min_x=1, max_x=5, min_y=1, max_y=4)
print(hits)
```

## Interval Tree

Use the interval tree when you need to track 1D geometric extents, for example the active x-ranges of projected segments in a sweep-line algorithm.

```python
from compgeom import Interval, IntervalTree

tree = IntervalTree([
    Interval(0.0, 2.5, "segment_ab"),
    Interval(1.5, 4.0, "segment_cd"),
    Interval(3.0, 5.5, "segment_ef"),
])

print(tree.query_point(2.0))
print(tree.query_interval(2.0, 3.5))
```

## Segment Tree

Use the segment tree when you need fast range aggregation over a 1D discretization, such as occupancy counts on scanline slabs or height samples along a terrain profile.

```python
from compgeom import SegmentTree

tree = SegmentTree.for_sum([3, 1, 0, 2, 4, 1])
print(tree.range_query(1, 4))

tree.update(2, 5)
print(tree.range_query(1, 4))
```

## Notes

- `range_search` assumes the KD-tree was built with `build_kdtree`.
- `IntervalTree` accepts either `Interval` instances or tuples like `(start, end)` and `(start, end, payload)`.
- `SegmentTree` exposes helper constructors for sum, min, and max queries:
  - `SegmentTree.for_sum(values)`
  - `SegmentTree.for_min(values)`
  - `SegmentTree.for_max(values)`
