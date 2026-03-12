import pytest
import math
from compgeom.kernel import Point
from compgeom.polygon.polygon_smoothing import PolygonalMeanCurvatureFlow

def test_resample_polygon():
    # Square: (0,0), (1,0), (1,1), (0,1)
    poly = [Point(0, 0), Point(1, 0), Point(1, 1), Point(0, 1)]
    resampled = PolygonalMeanCurvatureFlow.resample_polygon(poly, 8)
    assert len(resampled) == 8
    # Perimeter is 4.0, interval is 0.5.
    # Points should be (0,0), (0.5,0), (1,0), (1,0.5), (1,1), (0.5,1), (0,1), (0,0.5)
    assert resampled[1].x == pytest.approx(0.5)
    assert resampled[1].y == pytest.approx(0.0)
    assert resampled[3].x == pytest.approx(1.0)
    assert resampled[3].y == pytest.approx(0.5)

def test_smooth_polygon():
    # A very irregular polygon
    poly = [Point(0, 0), Point(10, 0), Point(10, 10), Point(5, 5), Point(0, 10)]
    smoothed = PolygonalMeanCurvatureFlow.smooth(poly, iterations=10)
    assert len(smoothed) == len(poly)
    # Check if it's still a valid polygon
    assert all(isinstance(p, Point) for p in smoothed)

def test_smooth_polygon_no_drift():
    poly = [Point(0, 0), Point(1, 0), Point(1, 1), Point(0, 1)]
    smoothed = PolygonalMeanCurvatureFlow.smooth(poly, iterations=5, fix_centroid=True)
    # Centroid should be (0,0)
    cx = sum(p.x for p in smoothed) / len(smoothed)
    cy = sum(p.y for p in smoothed) / len(smoothed)
    assert cx == pytest.approx(0.0)
    assert cy == pytest.approx(0.0)
