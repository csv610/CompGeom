"""Unit tests for Computational Algebraic Geometry module."""
import pytest
import numpy as np
from compgeom.algebraic import MultivariatePolynomial, GrobnerBasis, Resultant

def test_polynomial_arithmetic():
    # (x + y) * (x - y) = x^2 - y^2
    # x is (1, 0), y is (0, 1)
    x = MultivariatePolynomial({(1, 0): 1.0}, num_vars=2)
    y = MultivariatePolynomial({(0, 1): 1.0}, num_vars=2)
    
    p1 = x + y
    p2 = x - y
    res = p1 * p2
    
    # Expected: x^2 - y^2 -> {(2, 0): 1.0, (0, 2): -1.0}
    assert len(res.terms) == 2
    assert res.terms[(2, 0)] == pytest.approx(1.0)
    assert res.terms[(0, 2)] == pytest.approx(-1.0)

def test_grobner_basis_simple():
    # Intersection of x + y - 1 = 0 and x - y = 0
    # Expected: x = 0.5, y = 0.5
    f1 = MultivariatePolynomial({(1, 0): 1.0, (0, 1): 1.0, (0, 0): -1.0}, num_vars=2)
    f2 = MultivariatePolynomial({(1, 0): 1.0, (0, 1): -1.0}, num_vars=2)
    
    basis = GrobnerBasis.solve([f1, f2], order='lex')
    
    # The reduced lex basis should be {x - 0.5, y - 0.5} or similar
    # With lexicographical order (x > y):
    # f2: x - y = 0
    # f1 - f2: 2y - 1 = 0 -> y - 0.5 = 0
    
    # Check if we have a polynomial that is only in y
    found_y = False
    for p in basis:
        if (1, 0) not in p.terms and (0, 1) in p.terms:
            # Should be y - 0.5
            assert p.terms[(0, 1)] == pytest.approx(1.0)
            assert p.terms[(0, 0)] == pytest.approx(-0.5)
            found_y = True
    assert found_y

def test_resultant_identity():
    # f = x^2 - 1, g = x - 1
    # They share root x = 1, so resultant should be 0.
    f_coeffs = [-1.0, 0.0, 1.0] # 1x^2 + 0x - 1
    g_coeffs = [-1.0, 1.0]      # 1x - 1
    
    res = Resultant.compute(f_coeffs, g_coeffs)
    assert abs(res) < 1e-9
