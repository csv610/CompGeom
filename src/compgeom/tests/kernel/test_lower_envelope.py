import pytest
from compgeom.kernel import Point2D
from compgeom.algo.lower_envelop import DavenportSchinzel, EnvelopeSegment

def test_lower_envelope_single_segment():
    segments = [(Point2D(0, 0), Point2D(10, 10))]
    env = DavenportSchinzel.lower_envelope_segments(segments)
    assert len(env) == 1
    assert env[0].slope == 1.0
    assert env[0].intercept == 0.0

def test_lower_envelope_two_intersecting_segments():
    # Segments y=1 and y=x (intersect at x=1)
    s1 = (Point2D(0, 1), Point2D(10, 1))
    s2 = (Point2D(0, 0), Point2D(10, 10))
    env = DavenportSchinzel.lower_envelope_segments([s1, s2])
    # Lower envelope should be y=x for x in [0, 1] and y=1 for x in [1, 10]
    assert len(env) >= 2
    # First part (y=x)
    assert env[0].slope == 1.0
    assert env[0].x_start == 0.0
    assert env[0].x_end == pytest.approx(1.0)
    # Second part (y=1)
    assert env[-1].slope == 0.0
    assert env[-1].x_start == pytest.approx(1.0)
    assert env[-1].x_end == 10.0

def test_calculate_sequence():
    s1 = (Point2D(0, 1), Point2D(10, 1))
    s2 = (Point2D(0, 0), Point2D(10, 10))
    # Order of segments: s2 (id=1) then s1 (id=0)
    seq = DavenportSchinzel.calculate_sequence([s1, s2])
    assert seq == [1, 0]

def test_lower_envelope_empty():
    assert DavenportSchinzel.lower_envelope_segments([]) == []

def test_envelope_segment_y_at():
    seg = EnvelopeSegment(0, 10, 2.0, 5.0, 1)
    assert seg.y_at(5) == 15.0
