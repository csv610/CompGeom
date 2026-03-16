import pytest
import math
from compgeom.kernel import Point2D
from compgeom.polygon import Polygon, fourier_smooth_polygon

def test_fourier_smoothing():
    # 1. Create a noisy square
    noisy_square = [
        Point2D(0,0), Point2D(5, 0.1), Point2D(10,0),
        Point2D(10.1, 5), Point2D(10,10),
        Point2D(5, 9.9), Point2D(0,10),
        Point2D(-0.1, 5)
    ]

    # Apply Fourier smoothing
    # With very few harmonics, it should look like a circle/ellipse
    smoothed_3 = fourier_smooth_polygon(noisy_square, n_harmonics=2, resample_points=64)
    assert len(smoothed_3) == 64
    
    # Check if smoothed vertices are Point2D objects
    assert all(isinstance(v, Point2D) for v in smoothed_3)
    
    # 2. More harmonics = better fit
    smoothed_10 = fourier_smooth_polygon(noisy_square, n_harmonics=10, resample_points=64)
    assert len(smoothed_10) == 64

if __name__ == "__main__":
    test_fourier_smoothing()
