import math
import pytest
from compgeom.kernel import Point2D
from compgeom.polygon import Polygon, approximate_polygon_polynomial
from compgeom.polygon.polygon_polynomial import evaluate_polynomial

def test_approximate_polynomials_returns_empty_coefficients_for_empty_polygon():
    polygon = Polygon([])
    x_coeffs, y_coeffs = approximate_polygon_polynomial(polygon, order=3)
    assert x_coeffs == []
    assert y_coeffs == []

def test_approximate_polynomials_wrapper_matches_order():
    polygon = Polygon([Point2D(0, 0), Point2D(10, 0), Point2D(10, 10), Point2D(0, 10)])

    wrapper_x, wrapper_y = approximate_polygon_polynomial(polygon, order=2)

    assert len(wrapper_x) == 3
    assert len(wrapper_y) == 3
    assert all(math.isfinite(value) for value in wrapper_x + wrapper_y)

def test_order_zero_polynomial_fit():
    polygon = Polygon([Point2D(0, 0), Point2D(10, 0), Point2D(10, 10), Point2D(0, 10)])

    x_coeffs, y_coeffs = approximate_polygon_polynomial(polygon, order=0)

    # For a square (0,0)-(10,0)-(10,10)-(0,10)-(0,0)
    # Average x: (0+10+10+0+0)/5 = 20/5 = 4.0
    # Average y: (0+0+10+10+0)/5 = 20/5 = 4.0
    # zip(t_values, x_values, y_values) for order 0:
    # m = 1. matrix[0][0] = sum(tk^0) = count = 5.
    # rhs_x[0] = sum(xk) = 0+10+10+0+0 = 20.
    # x_coeffs[0] = 20/5 = 4.0.
    assert x_coeffs == [4.0]
    assert y_coeffs == [4.0]
    assert evaluate_polynomial(x_coeffs, 0.0) == 4.0
    assert evaluate_polynomial(x_coeffs, 0.5) == 4.0
    assert evaluate_polynomial(y_coeffs, 1.0) == 4.0
