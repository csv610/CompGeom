import pytest
from compgeom.kernel import Point2D
from compgeom.polygon import Polygon, approximate_polygon_polynomial

def test_polynomial_approx():
    # 1. Square
    poly = Polygon([Point2D(0,0), Point2D(10,0), Point2D(10,10), Point2D(0,10)])
    
    # Low order approximation (order 2)
    x_coeffs, y_coeffs = approximate_polygon_polynomial(poly, order=2)
    assert len(x_coeffs) == 3
    assert len(y_coeffs) == 3
    
    # Higher order
    x_coeffs_6, y_coeffs_6 = approximate_polygon_polynomial(poly, order=6)
    assert len(x_coeffs_6) == 7
    assert len(y_coeffs_6) == 7

if __name__ == "__main__":
    test_polynomial_approx()
