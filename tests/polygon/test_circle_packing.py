from compgeom.kernel import Point2D
from compgeom.polygon.circle_packing import (
    pack_circles,
    optimal_radius,
    CirclePackingResult,
    visualize_circle_packing,
)


def test_circle_packer_pack():
    polygon = [Point2D(0, 0), Point2D(10, 0), Point2D(10, 10), Point2D(0, 10)]
    radius = 1.0
    result = pack_circles(polygon, radius)
    assert isinstance(result, CirclePackingResult)
    centers = result.centers
    assert len(centers) > 0
    for center in centers:
        assert center.x >= 1.0 - 1e-9
        assert center.x <= 9.0 + 1e-9
        assert center.y >= 1.0 - 1e-9
        assert center.y <= 9.0 + 1e-9


def test_circle_packer_pack_empty():
    polygon = []
    result = pack_circles(polygon, 1.0)
    assert result.centers == []


def test_circle_packer_pack_invalid_radius():
    polygon = [Point2D(0, 0), Point2D(10, 0), Point2D(10, 10), Point2D(0, 10)]
    result = pack_circles(polygon, -1.0)
    assert result.centers == []


def test_circle_packer_optimal_radius():
    polygon = [Point2D(0, 0), Point2D(10, 0), Point2D(10, 10), Point2D(0, 10)]
    num_circles = 4
    radius = optimal_radius(polygon, num_circles)
    assert radius > 0
    result = pack_circles(polygon, radius)
    assert len(result.centers) >= num_circles


def test_circle_packer_optimal_radius_empty():
    radius = optimal_radius([], 4)
    assert radius == 0.0


def test_circle_packer_result_contains_radius():
    polygon = [Point2D(0, 0), Point2D(10, 0), Point2D(10, 10), Point2D(0, 10)]
    radius = 2.5
    result = pack_circles(polygon, radius)
    assert result.radius == radius


def test_circle_packer_visualize():
    polygon = [Point2D(0, 0), Point2D(10, 0), Point2D(10, 10), Point2D(0, 10)]
    centers = [Point2D(5, 5)]
    svg = visualize_circle_packing(polygon, centers, 2.0)
    assert "<svg" in svg
    assert "</svg>" in svg
