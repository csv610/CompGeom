import pytest
import math
from compgeom.segment.random_rays import RandomRayGenerator
from compgeom.segment.random_segments import RandomSegmentGenerator


def test_random_ray_generator_creation():
    gen = RandomRayGenerator(radius=10.0, min_gap=0.5)
    assert gen.radius == 10.0
    assert gen.min_gap == 0.5
    assert len(gen.rays) == 0


def test_random_ray_generator_with_seed():
    gen = RandomRayGenerator(radius=10.0, min_gap=0.5, seed=42)
    rays = gen.generate(5)
    assert len(rays) <= 5
    for r in rays:
        assert len(r) == 4
        ox, oy, p2x, p2y = r
        dist = math.hypot(p2x - ox, p2y - oy)
        assert dist > 0


def test_random_ray_generator_circle_constraint():
    gen = RandomRayGenerator(radius=10.0, min_gap=0.5, seed=123)
    rays = gen.generate(3)
    for r in rays:
        ox, oy, p2x, p2y = r
        assert ox**2 + oy**2 <= (10.0 * 2.0) ** 2
        assert p2x**2 + p2y**2 <= (10.0 * 2.0) ** 2


def test_random_ray_generator_clearance():
    gen = RandomRayGenerator(radius=10.0, min_gap=2.0, seed=456)
    rays = gen.generate(5)
    if len(rays) > 1:
        for i in range(len(rays)):
            for j in range(i + 1, len(rays)):
                r1, r2 = rays[i], rays[j]
                dist = math.hypot(r1[0] - r2[0], r1[1] - r2[1])
                assert dist >= 2.0 or dist == 0


def test_random_ray_generator_empty():
    gen = RandomRayGenerator(radius=1.0, min_gap=5.0, seed=789)
    rays = gen.generate(10)
    assert len(rays) <= 10


def test_random_segment_generator_creation():
    gen = RandomSegmentGenerator(radius=10.0, min_gap=0.5)
    assert gen.radius == 10.0
    assert gen.min_gap == 0.5
    assert len(gen.segments) == 0


def test_random_segment_generator_with_seed():
    gen = RandomSegmentGenerator(radius=10.0, min_gap=0.5, seed=42)
    segs = gen.generate(5, min_len=1.0, max_len=3.0)
    assert len(segs) <= 5
    for s in segs:
        assert len(s) == 4
        x1, y1, x2, y2 = s
        length = math.hypot(x2 - x1, y2 - y1)
        assert 1.0 <= length <= 3.0


def test_random_segment_generator_circle_constraint():
    gen = RandomSegmentGenerator(radius=10.0, min_gap=0.5, seed=123)
    segs = gen.generate(3, min_len=1.0, max_len=5.0)
    safe_r = 10.0 - 0.5
    for s in segs:
        x1, y1, x2, y2 = s
        assert x1**2 + y1**2 <= safe_r**2
        assert x2**2 + y2**2 <= safe_r**2


def test_random_segment_generator_clearance():
    gen = RandomSegmentGenerator(radius=10.0, min_gap=1.5, seed=456)
    segs = gen.generate(5, min_len=1.0, max_len=3.0)
    if len(segs) > 1:
        for i in range(len(segs)):
            for j in range(i + 1, len(segs)):
                s1, s2 = segs[i], segs[j]
                d1 = math.hypot(s1[0] - s2[0], s1[1] - s2[1])
                d2 = math.hypot(s1[0] - s2[2], s1[1] - s2[3])
                d3 = math.hypot(s1[2] - s2[0], s1[3] - s2[1])
                d4 = math.hypot(s1[2] - s2[2], s1[3] - s2[3])
                min_dist = min(d1, d2, d3, d4)
                assert min_dist >= 1.5 or min_dist == 0


def test_random_segment_generator_gap_too_large():
    gen = RandomSegmentGenerator(radius=10.0, min_gap=15.0, seed=789)
    with pytest.raises(ValueError):
        gen.generate(1, min_len=1.0, max_len=3.0)


def test_random_segment_generator_empty():
    gen = RandomSegmentGenerator(radius=1.0, min_gap=2.9, seed=999)
    with pytest.raises(ValueError, match="Gap too large"):
        gen.generate(1, min_len=0.5, max_len=1.0)
