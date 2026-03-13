import math

from compgeom.kernel import Point2D
from compgeom.polygon import Polygon, approximate_polynomials
from compgeom.polygon.polygon_polynomial import evaluate_polynomial


def test_approximate_polynomials_returns_empty_coefficients_for_empty_polygon():
    polygon = Polygon([])

    x_coeffs, y_coeffs = polygon.approximate_polynomials(order=3)

    assert x_coeffs == []
    assert y_coeffs == []


def test_approximate_polynomials_wrapper_matches_polygon_method_and_order():
    polygon = Polygon([Point2D(0, 0), Point2D(10, 0), Point2D(10, 10), Point2D(0, 10)])

    method_x, method_y = polygon.approximate_polynomials(order=2)
    wrapper_x, wrapper_y = approximate_polynomials(polygon, order=2)

    assert wrapper_x == method_x
    assert wrapper_y == method_y
    assert len(method_x) == 3
    assert len(method_y) == 3
    assert all(math.isfinite(value) for value in method_x + method_y)


def test_order_zero_polynomial_fit_matches_closed_loop_sample_average():
    polygon = Polygon([Point2D(0, 0), Point2D(10, 0), Point2D(10, 10), Point2D(0, 10)])

    x_coeffs, y_coeffs = approximate_polynomials(polygon, order=0)

    assert x_coeffs == [4.0]
    assert y_coeffs == [4.0]
    assert evaluate_polynomial(x_coeffs, 0.0) == 4.0
    assert evaluate_polynomial(x_coeffs, 0.5) == 4.0
    assert evaluate_polynomial(y_coeffs, 1.0) == 4.0
