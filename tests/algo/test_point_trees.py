
import pytest
from compgeom.kernel import Point2D, Point3D
from compgeom.algo import point_trees

def test_point_quadtree():
    qt = point_trees.PointQuadtree()
    points = [Point2D(0, 0), Point2D(1, 1), Point2D(-1, -1), Point2D(1, -1), Point2D(-1, 1)]
    for p in points:
        assert qt.insert(p) is True
    assert qt.count == 5
    # Redundant insert
    assert qt.insert(Point2D(0, 0)) is False
    assert qt.count == 5

def test_kdtree():
    points = [Point2D(x, y) for x in range(5) for y in range(5)]
    root = point_trees.build_kdtree(points)
    assert root is not None
    
    # Range search
    res = point_trees.range_search(root, 1.5, 3.5, 1.5, 3.5)
    # Should find (2,2), (2,3), (3,2), (3,3)
    assert len(res) == 4
    pts = {(p.x, p.y) for p in res}
    assert (2, 2) in pts
    assert (3, 3) in pts

def test_interval_tree():
    intervals = [(0, 10, "A"), (5, 15, "B"), (20, 30, "C")]
    it = point_trees.IntervalTree(intervals)
    
    # Query point
    res1 = it.query_point(7)
    assert len(res1) == 2
    payloads = {iv.payload for iv in res1}
    assert "A" in payloads
    assert "B" in payloads
    
    # Query interval
    res2 = it.query_interval(12, 22)
    assert len(res2) == 2
    payloads2 = {iv.payload for iv in res2}
    assert "B" in payloads2
    assert "C" in payloads2

def test_segment_tree():
    values = [1, 2, 3, 4, 5]
    st = point_trees.SegmentTree.for_sum(values)
    assert st.range_query(0, 4) == 15
    assert st.range_query(1, 3) == 9
    
    st.update(2, 10) # [1, 2, 10, 4, 5]
    assert st.range_query(1, 3) == 16
    
    st_min = point_trees.SegmentTree.for_min(values)
    assert st_min.range_query(0, 4) == 1
    
    st_max = point_trees.SegmentTree.for_max(values)
    assert st_max.range_query(0, 4) == 5

def test_point_simplifier_2d():
    points = [Point2D(0, 0), Point2D(0.01, 0.01), Point2D(10, 10), Point2D(10.01, 10.01)]
    # With a small ratio, only (0,0) and (10,10) should remain approximately
    simplified = point_trees.PointSimplifier.simplify(points, ratio=0.1)
    assert len(simplified) < 4
    assert len(simplified) >= 2

def test_point_simplifier_3d():
    points = [Point3D(0, 0, 0), Point3D(0.01, 0.01, 0.01), Point3D(10, 10, 10)]
    simplified = point_trees.PointSimplifier.simplify(points, ratio=0.1)
    assert len(simplified) == 2

def test_point_simplifier_protected():
    p1 = Point2D(0, 0, id=1)
    p2 = Point2D(0.01, 0.01, id=2)
    simplified = point_trees.PointSimplifier.simplify([p1, p2], ratio=0.5, protected_ids={1, 2})
    assert len(simplified) == 2
