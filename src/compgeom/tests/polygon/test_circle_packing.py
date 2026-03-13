from compgeom.kernel import Point2D
from compgeom.polygon.circle_packing import CirclePacker

def test_circle_packer_pack():
    polygon = [Point2D(0, 0), Point2D(10, 0), Point2D(10, 10), Point2D(0, 10)]
    radius = 1.0
    centers = CirclePacker.pack(polygon, radius)
    # With a 10x10 square and radius 1.0, some circles should fit.
    assert len(centers) > 0
    # All centers should be at least `radius` distance from edges.
    for center in centers:
        assert center.x >= 1.0 - 1e-9
        assert center.x <= 9.0 + 1e-9
        assert center.y >= 1.0 - 1e-9
        assert center.y <= 9.0 + 1e-9

def test_circle_packer_pack_empty():
    polygon = []
    centers = CirclePacker.pack(polygon, 1.0)
    assert centers == []

def test_circle_packer_pack_invalid_radius():
    polygon = [Point2D(0, 0), Point2D(10, 0), Point2D(10, 10), Point2D(0, 10)]
    centers = CirclePacker.pack(polygon, -1.0)
    assert centers == []

def test_circle_packer_optimal_radius():
    polygon = [Point2D(0, 0), Point2D(10, 0), Point2D(10, 10), Point2D(0, 10)]
    num_circles = 4
    radius = CirclePacker.optimal_radius(polygon, num_circles)
    assert radius > 0
    centers = CirclePacker.pack(polygon, radius)
    assert len(centers) >= num_circles

def test_circle_packer_optimal_radius_empty():
    radius = CirclePacker.optimal_radius([], 4)
    assert radius == 0.0

def test_circle_packer_calculate_efficiency():
    polygon = [Point2D(0, 0), Point2D(10, 0), Point2D(10, 10), Point2D(0, 10)]
    centers = [Point2D(5, 5)]
    radius = 2.0
    efficiency = CirclePacker.calculate_efficiency(polygon, centers, radius)
    # Area of polygon = 100
    # Area of 1 circle = pi * 4 = 12.566
    # Efficiency = 12.566%
    assert 12.0 < efficiency < 13.0

def test_circle_packer_visualize():
    polygon = [Point2D(0, 0), Point2D(10, 0), Point2D(10, 10), Point2D(0, 10)]
    centers = [Point2D(5, 5)]
    svg = CirclePacker.visualize(polygon, centers, 2.0)
    assert "<svg" in svg
    assert "</svg>" in svg
