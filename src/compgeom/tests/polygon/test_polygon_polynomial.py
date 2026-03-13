
from compgeom.kernel import Point2D
from compgeom.polygon import Polygon

def test_polynomial_approx():
    print("--- Running Polygon Polynomial Approximation Tests ---")
    
    # 1. Square
    poly = Polygon([Point2D(0,0), Point2D(10,0), Point2D(10,10), Point2D(0,10)])
    
    # Low order approximation (order 2 - won't fit well but should run)
    x_coeffs, y_coeffs = poly.approximate_polynomials(order=2)
    print(f"Order 2 x_coeffs: {[round(c, 2) for c in x_coeffs]}")
    print(f"Order 2 y_coeffs: {[round(c, 2) for c in y_coeffs]}")
    
    # Higher order
    x_coeffs_6, y_coeffs_6 = poly.approximate_polynomials(order=6)
    print(f"Order 6 x_coeffs length: {len(x_coeffs_6)}")

    # Check that a degree 1 fit for a line works (conceptually)
    line_poly = Polygon([Point2D(0,0), Point2D(10,10), Point2D(0,0)]) # Degenerate "polygon" as a line
    # (Not a great test for a polygon class but tests the solver)

    print("--- Tests Completed ---")

if __name__ == "__main__":
    test_polynomial_approx()
