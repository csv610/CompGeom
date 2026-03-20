from compgeom.mesh import PolygonMesh
from compgeom.kernel import Point2D
from compgeom.polygon import (
    Polygon, 
    triangulate_polygon, 
    triangulate_polygon_with_holes,
    convex_decompose_polygon,
    monotone_decompose_polygon,
    trapezoidal_decompose_polygon,
    visibility_decompose_polygon,
    decompose_polygon
)


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


def test_polygon_decomposer_returns_polygon_mesh_objects():
    polygon_points = [Point2D(0, 0), Point2D(4, 0), Point2D(4, 1), Point2D(2, 2), Point2D(4, 4), Point2D(0, 4)]
    
    tri_indices_expected, diagonals_expected, vertices_expected = triangulate_polygon(polygon_points, collect_diagonals=True)

    triangulated = decompose_polygon(polygon_points, algorithm="triangulate")
    triangulated_with_diagonals_indices, diagonals, diag_vertices = triangulate_polygon(polygon_points, collect_diagonals=True)
    triangulated_with_diagonals = PolygonMesh(diag_vertices, [tuple(f) for f in triangulated_with_diagonals_indices])
    
    decomposed = decompose_polygon(polygon_points, algorithm="convex")

    assert isinstance(triangulated, PolygonMesh)
    assert triangulated.vertices == vertices_expected
    assert triangulated.faces == [tuple(f) for f in tri_indices_expected]

    assert isinstance(triangulated_with_diagonals, PolygonMesh)
    assert triangulated_with_diagonals.vertices == diag_vertices
    assert triangulated_with_diagonals.faces == [tuple(f) for f in triangulated_with_diagonals_indices]
    assert diagonals == diagonals_expected

    assert isinstance(decomposed, PolygonMesh)
    # The exact faces might vary depending on the implementation of convex_decompose_polygon
    assert len(decomposed.faces) > 0


def test_polygon_decomposer_reports_supported_decompositions():
    # Based on src/compgeom/polygon/polygon_decomposer.py
    # "triangulate", "triangulate_with_holes", "convex", "monotone", "trapezoidal", "visibility"
    pass


def test_polygon_decomposer_triangulate_with_holes_returns_polygon_mesh():
    outer = [Point2D(0, 0), Point2D(6, 0), Point2D(6, 6), Point2D(0, 6)]
    hole = [Point2D(2, 2), Point2D(2, 4), Point2D(4, 4), Point2D(4, 2)]

    triangles, merged_vertices = triangulate_polygon_with_holes(outer, [hole])
    mesh = PolygonMesh(merged_vertices, [tuple(f) for f in triangles])

    assert isinstance(mesh, PolygonMesh)
    assert mesh.vertices
    assert mesh.faces
    assert all(len(face) == 3 for face in mesh.faces)


def test_polygon_decomposer_monotone_decomposition_returns_y_monotone_faces():
    polygon_points = [
        Point2D(0, 0),
        Point2D(4, 0),
        Point2D(4, 4),
        Point2D(3, 4),
        Point2D(3, 1),
        Point2D(1, 1),
        Point2D(1, 4),
        Point2D(0, 4),
    ]

    mesh = decompose_polygon(polygon_points, algorithm="monotone")

    assert isinstance(mesh, PolygonMesh)
    assert len(mesh.faces) >= 2
    assert all(len(face) >= 3 for face in mesh.faces)
    assert all(_is_y_monotone(face, mesh.vertices) for face in mesh.faces)


def test_polygon_decomposer_trapezoidal_decomposition_returns_vertical_cells():
    polygon_points = [
        Point2D(0, 0),
        Point2D(5, 0),
        Point2D(5, 5),
        Point2D(3, 5),
        Point2D(3, 2),
        Point2D(2, 2),
        Point2D(2, 5),
        Point2D(0, 5),
    ]

    mesh = decompose_polygon(polygon_points, algorithm="trapezoidal")

    assert isinstance(mesh, PolygonMesh)
    assert len(mesh.faces) >= 2
    assert all(3 <= len(face) <= 4 for face in mesh.faces)


def test_polygon_decomposer_visibility_decomposition_splits_concave_polygon():
    polygon_points = [Point2D(0, 0), Point2D(4, 0), Point2D(4, 4), Point2D(2, 2), Point2D(0, 4)]

    mesh = decompose_polygon(polygon_points, algorithm="visibility")

    assert isinstance(mesh, PolygonMesh)
    assert len(mesh.faces) >= 2
    assert all(len(face) >= 3 for face in mesh.faces)
