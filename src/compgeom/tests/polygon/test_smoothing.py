import pytest
import math
from compgeom.kernel import Point2D
from compgeom.polygon.polygon_smoothing import resample_polygon, mean_curvature_flow_polygon

def test_resample_polygon():
    # Square: (0,0), (1,0), (1,1), (0,1)
    poly = [Point2D(0, 0), Point2D(1, 0), Point2D(1, 1), Point2D(0, 1)]
    resampled = resample_polygon(poly, 8)
    assert len(resampled) == 8
    # Perimeter is 4.0, interval is 0.5.
    # Points should be (0,0), (0.5,0), (1,0), (1,0.5), (1,1), (0.5,1), (0,1), (0,0.5)
    assert resampled[1].x == pytest.approx(0.5)
    assert resampled[1].y == pytest.approx(0.0)
    assert resampled[3].x == pytest.approx(1.0)
    assert resampled[3].y == pytest.approx(0.5)

def test_smooth_polygon():
    # A very irregular polygon
    poly = [Point2D(0, 0), Point2D(10, 0), Point2D(10, 10), Point2D(5, 5), Point2D(0, 10)]
    smoothed = mean_curvature_flow_polygon(poly, iterations=10)
    assert len(smoothed) == len(poly)
    # Check if it's still a valid polygon
    assert all(isinstance(p, Point2D) for p in smoothed)

def test_smooth_polygon_no_drift():
    poly = [Point2D(0, 0), Point2D(1, 0), Point2D(1, 1), Point2D(0, 1)]
    smoothed = mean_curvature_flow_polygon(poly, iterations=5, fix_centroid=True)
    # Centroid should be (0,0)
    cx = sum(p.x for p in smoothed) / len(smoothed)
    cy = sum(p.y for p in smoothed) / len(smoothed)
    assert cx == pytest.approx(0.0)
    assert cy == pytest.approx(0.0)
