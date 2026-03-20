
import pytest
from compgeom.kernel import Point2D
from compgeom.algo.lower_envelop import DavenportSchinzel, EnvelopeSegment

def test_lower_envelope_empty():
    assert DavenportSchinzel.lower_envelope_segments([]) == []
    assert DavenportSchinzel.calculate_sequence([]) == []

def test_lower_envelope_single():
    p1 = Point2D(0, 0)
    p2 = Point2D(10, 10)
    res = DavenportSchinzel.lower_envelope_segments([(p1, p2)])
    assert len(res) == 1
    assert res[0].x_start == 0
    assert res[0].x_end == 10
    assert res[0].slope == 1.0
    assert res[0].intercept == 0.0

def test_lower_envelope_non_intersecting():
    # Two segments, one strictly below the other
    s1 = (Point2D(0, 0), Point2D(10, 0)) # y = 0
    s2 = (Point2D(0, 5), Point2D(10, 5)) # y = 5
    
    res = DavenportSchinzel.lower_envelope_segments([s1, s2])
    assert len(res) == 1
    assert res[0].segment_id == 0
    assert res[0].y_at(5) == 0.0

def test_lower_envelope_intersecting():
    # Two segments that intersect at x=5
    # s1: y = x (0 to 10)
    # s2: y = 10 - x (0 to 10)
    # Lower envelope should be s1 from 0 to 5, and s2 from 5 to 10.
    # Wait, y=x at x=2 is 2. y=10-x at x=2 is 8. So s1 is lower for x < 5.
    # At x=8, y=x is 8, y=10-x is 2. So s2 is lower for x > 5.
    s1 = (Point2D(0, 0), Point2D(10, 10))
    s2 = (Point2D(0, 10), Point2D(10, 0))
    
    res = DavenportSchinzel.lower_envelope_segments([s1, s2])
    assert len(res) == 2
    assert res[0].segment_id == 0
    assert res[0].x_start == 0
    assert res[0].x_end == pytest.approx(5.0)
    assert res[1].segment_id == 1
    assert res[1].x_start == pytest.approx(5.0)
    assert res[1].x_end == 10.0
    
    seq = DavenportSchinzel.calculate_sequence([s1, s2])
    assert seq == [0, 1]

def test_lower_envelope_partial_overlap():
    # s1: x from 0 to 5, y = 0
    # s2: x from 3 to 10, y = -1
    s1 = (Point2D(0, 0), Point2D(5, 0))
    s2 = (Point2D(3, -1), Point2D(10, -1))
    
    res = DavenportSchinzel.lower_envelope_segments([s1, s2])
    # x: 0 to 3 -> s1
    # x: 3 to 10 -> s2
    assert len(res) == 2
    assert res[0].segment_id == 0
    assert res[0].x_end == pytest.approx(3.0)
    assert res[1].segment_id == 1
    assert res[1].x_start == pytest.approx(3.0)

def test_envelope_segment_y_at():
    seg = EnvelopeSegment(0, 10, 2.0, 5.0, 0)
    assert seg.y_at(0) == 5.0
    assert seg.y_at(5) == 15.0
    assert seg.y_at(10) == 25.0
