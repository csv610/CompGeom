import pytest
from compgeom.point import (
    HaltonPointsGenerator,
    SobolPointsGenerator,
    HammersleyPointsGenerator,
    LatinHypercubeGenerator,
)


def test_halton_generator():
    gen = HaltonPointsGenerator(dimensions=2)
    pts = gen.generate(10)
    assert len(pts) == 10
    for p in pts:
        assert 0 <= p[0] <= 1
        assert 0 <= p[1] <= 1


def test_halton_with_bounds():
    gen = HaltonPointsGenerator(dimensions=2, box_min=[0, 0], box_max=[10, 20])
    pts = gen.generate(5)
    for p in pts:
        assert 0 <= p[0] <= 10
        assert 0 <= p[1] <= 20


def test_sobol_generator():
    gen = SobolPointsGenerator(dimensions=2)
    pts = gen.generate(10)
    assert len(pts) == 10
    for p in pts:
        assert 0 <= p[0] <= 1
        assert 0 <= p[1] <= 1


def test_sobol_with_bounds():
    gen = SobolPointsGenerator(dimensions=2, box_min=[-5, 0], box_max=[5, 10])
    pts = gen.generate(5)
    for p in pts:
        assert -5 <= p[0] <= 5
        assert 0 <= p[1] <= 10


def test_hammersley_generator():
    gen = HammersleyPointsGenerator(dimensions=2)
    pts = gen.generate(10)
    assert len(pts) == 10
    for p in pts:
        assert 0 <= p[0] <= 1
        assert 0 <= p[1] <= 1


def test_hammersley_with_bounds():
    gen = HammersleyPointsGenerator(dimensions=2, box_min=[0, 0], box_max=[100, 50])
    pts = gen.generate(5)
    for p in pts:
        assert 0 <= p[0] <= 100
        assert 0 <= p[1] <= 50


def test_latin_hypercube_generator():
    gen = LatinHypercubeGenerator(dimensions=2)
    pts = gen.generate(10)
    assert len(pts) == 10
    for p in pts:
        assert 0 <= p[0] <= 1
        assert 0 <= p[1] <= 1


def test_latin_hypercube_with_bounds():
    gen = LatinHypercubeGenerator(dimensions=2, box_min=[-10, 0], box_max=[10, 100])
    pts = gen.generate(5)
    for p in pts:
        assert -10 <= p[0] <= 10
        assert 0 <= p[1] <= 100


def test_latin_hypercube_seed():
    gen = LatinHypercubeGenerator(dimensions=2)
    pts1 = gen.generate(5, seed=42)
    pts2 = gen.generate(5, seed=42)
    assert pts1 == pts2
