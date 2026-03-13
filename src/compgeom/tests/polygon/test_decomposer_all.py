import pytest
from compgeom.mesh import PolygonMesh
from compgeom.kernel import Point2D
from compgeom.polygon import Polygon, PolygonDecomposer

def _is_y_monotone(face, vertices):
    if len(face) <= 3:
        return True

    top = max(range(len(face)), key=lambda i: (vertices[face[i]].y, -vertices[face[i]].x))
    bottom = min(range(len(face)), key=lambda i: (vertices[face[i]].y, vertices[face[i]].x))

    def chain(step):
        index = top
        ys = [vertices[face[index]].y]
        while index != bottom:
            index = (index + step) % len(face)
            ys.append(vertices[face[index]].y)
        return ys

    return all(
        ys[i] <= ys[i - 1] + 1e-9
        for ys in (chain(1), chain(-1))
        for i in range(1, len(ys))
    )

def test_ear_clip_triangulation():
    polygon_points = [Point2D(0, 0), Point2D(4, 0), Point2D(4, 4), Point2D(2, 2), Point2D(0, 4)]
    mesh = PolygonDecomposer.ear_clip_triangulation(polygon_points)
    assert isinstance(mesh, PolygonMesh)
    assert len(mesh.faces) == 3 # n-2 for simple polygon
    for face in mesh.faces:
        assert len(face) == 3

def test_triangulation_with_diagonals():
    polygon_points = [Point2D(0, 0), Point2D(4, 0), Point2D(4, 4), Point2D(2, 2), Point2D(0, 4)]
    mesh, diagonals = PolygonDecomposer.triangulation_with_diagonals(polygon_points)
    assert isinstance(mesh, PolygonMesh)
    assert len(diagonals) == 2 # n-3 diagonals
    assert len(mesh.faces) == 3

def test_triangulate_with_holes():
    outer = [Point2D(0, 0), Point2D(10, 0), Point2D(10, 10), Point2D(0, 10)]
    hole = [Point2D(4, 4), Point2D(4, 6), Point2D(6, 6), Point2D(6, 4)]
    mesh = PolygonDecomposer.triangulate_with_holes(outer, [hole])
    assert isinstance(mesh, PolygonMesh)
    # n_total = 8. Triangles = (n_outer + n_hole + 2*holes - 2) = 4 + 4 + 2 - 2 = 8? 
    # Actually with splicing, it becomes one polygon with n_outer + n_hole + 2 vertices.
    # n = 4 + 4 + 2 = 10. Triangles = 10 - 2 = 8.
    assert len(mesh.faces) == 8

def test_convex_decomposition():
    # L-shape
    polygon_points = [Point2D(0, 0), Point2D(2, 0), Point2D(2, 1), Point2D(1, 1), Point2D(1, 2), Point2D(0, 2)]
    mesh = PolygonDecomposer.convex_decomposition(polygon_points)
    assert isinstance(mesh, PolygonMesh)
    # Should be 2 convex pieces
    assert len(mesh.faces) == 2

def test_monotone_decomposition():
    # U-shape
    polygon_points = [
        Point2D(0, 0), Point2D(4, 0), Point2D(4, 4), Point2D(3, 4), 
        Point2D(3, 1), Point2D(1, 1), Point2D(1, 4), Point2D(0, 4)
    ]
    mesh = PolygonDecomposer.monotone_decomposition(polygon_points)
    assert isinstance(mesh, PolygonMesh)
    assert all(_is_y_monotone(face, mesh.vertices) for face in mesh.faces)

def test_trapezoidal_decomposition():
    polygon_points = [Point2D(0, 0), Point2D(4, 0), Point2D(4, 4), Point2D(2, 2), Point2D(0, 4)]
    mesh = PolygonDecomposer.trapezoidal_decomposition(polygon_points)
    assert isinstance(mesh, PolygonMesh)
    assert len(mesh.faces) > 0
    for face in mesh.faces:
        assert 3 <= len(face) <= 4

def test_visibility_decomposition():
    polygon_points = [Point2D(0, 0), Point2D(4, 0), Point2D(4, 4), Point2D(2, 2), Point2D(0, 4)]
    mesh = PolygonDecomposer.visibility_decomposition(polygon_points)
    assert isinstance(mesh, PolygonMesh)
    assert len(mesh.faces) >= 2

if __name__ == "__main__":
    pytest.main([__file__])
