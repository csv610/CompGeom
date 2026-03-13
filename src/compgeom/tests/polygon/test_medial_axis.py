import pytest
from compgeom.kernel import Point2D
from compgeom.polygon.medial_axis import sample_polygon_boundary, approximate_medial_axis

def test_sample_polygon_boundary():
    poly = [Point2D(0, 0), Point2D(1, 0), Point2D(1, 1), Point2D(0, 1)]
    samples = sample_polygon_boundary(poly, max_segment_length=0.5)
    # Each edge of length 1.0 split into 2 segments (4 edges * 2 = 8 samples)
    assert len(samples) >= 8

def test_approximate_medial_axis():
    poly = [Point2D(0, 0), Point2D(10, 0), Point2D(10, 10), Point2D(0, 10)]
    result = approximate_medial_axis(poly, resolution=2.0)
    assert "samples" in result
    assert "centers" in result
    assert "segments" in result
    # For a square, the medial axis should have some segments
    assert len(result["centers"]) > 0
