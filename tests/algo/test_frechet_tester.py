"""Unit tests for Sublinear Fréchet Tester."""
import pytest
import numpy as np
from compgeom.algo.frechet_tester import FrechetTester

def test_frechet_tester_identical():
    p = np.array([[0,0], [1,0], [2,0]])
    tester = FrechetTester(
        query_P=lambda i: p[i],
        query_Q=lambda j: p[j],
        n=len(p), m=len(p),
        delta=0.1, epsilon=0.1
    )
    assert tester.test() == "yes"

def test_frechet_tester_similar():
    p = np.array([[0,0], [1,0], [2,0]])
    q = np.array([[0,0.05], [1,0.05], [2,0.05]])
    tester = FrechetTester(
        query_P=lambda i: p[i],
        query_Q=lambda j: q[j],
        n=len(p), m=len(q),
        delta=0.1, epsilon=0.1
    )
    assert tester.test() == "yes"

def test_frechet_tester_far():
    p = np.array([[0,0], [1,0], [2,0]])
    q = np.array([[0,10], [1,10], [2,10]])
    tester = FrechetTester(
        query_P=lambda i: p[i],
        query_Q=lambda j: q[j],
        n=len(p), m=len(q),
        delta=1.0, epsilon=0.1
    )
    assert tester.test() == "no"
