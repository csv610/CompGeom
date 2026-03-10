from compgeom.mesh import PolygonMesh
from compgeom.geo_math.geometry import Point
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


def test_polygon_decomposer_returns_polygon_mesh_objects():
    polygon_points = [Point(0, 0), Point(4, 0), Point(4, 1), Point(2, 2), Point(4, 4), Point(0, 4)]
    polygon = Polygon(polygon_points)

    tri_indices_expected, tri_vertices_expected = PolygonDecomposer.triangulate_indices(polygon_points)
    diag_triangles_expected, diagonals_expected, diag_vertices_expected = (
        PolygonDecomposer.triangulation_with_diagonals_indices(polygon_points)
    )
    hm_partitions_expected, hm_vertices_expected = polygon.hertel_mehlhorn()

    triangulated = PolygonDecomposer.triangulate(polygon_points)
    triangulated_with_diagonals, diagonals = PolygonDecomposer.triangulation_with_diagonals(polygon_points)
    decomposed = PolygonDecomposer.convex_decomposition(polygon_points)

    assert isinstance(triangulated, PolygonMesh)
    assert triangulated.vertices == tri_vertices_expected
    assert triangulated.faces == tri_indices_expected

    assert isinstance(triangulated_with_diagonals, PolygonMesh)
    assert triangulated_with_diagonals.vertices == diag_vertices_expected
    assert triangulated_with_diagonals.faces == diag_triangles_expected
    assert diagonals == diagonals_expected

    assert PolygonDecomposer.convex_decomposition_indices(polygon_points) == (
        hm_partitions_expected,
        hm_vertices_expected,
    )
    assert isinstance(decomposed, PolygonMesh)
    assert decomposed.vertices == hm_vertices_expected
    assert decomposed.faces == [tuple(sorted(partition)) for partition in hm_partitions_expected]


def test_polygon_decomposer_reports_supported_decompositions():
    assert PolygonDecomposer.supported_decompositions() == [
        "triangulate",
        "triangulate_with_holes",
        "convex_decomposition",
        "monotone_decomposition",
        "trapezoidal_decomposition",
        "visibility_decomposition",
    ]


def test_polygon_decomposer_triangulate_with_holes_returns_polygon_mesh():
    outer = [Point(0, 0), Point(6, 0), Point(6, 6), Point(0, 6)]
    hole = [Point(2, 2), Point(2, 4), Point(4, 4), Point(4, 2)]

    mesh = PolygonDecomposer.triangulate_with_holes(outer, [hole])

    assert isinstance(mesh, PolygonMesh)
    assert mesh.vertices
    assert mesh.faces
    assert all(len(face) == 3 for face in mesh.faces)


def test_polygon_decomposer_monotone_decomposition_returns_y_monotone_faces():
    polygon_points = [
        Point(0, 0),
        Point(4, 0),
        Point(4, 4),
        Point(3, 4),
        Point(3, 1),
        Point(1, 1),
        Point(1, 4),
        Point(0, 4),
    ]

    mesh = PolygonDecomposer.monotone_decomposition(polygon_points)

    assert isinstance(mesh, PolygonMesh)
    assert len(mesh.faces) >= 2
    assert all(len(face) >= 3 for face in mesh.faces)
    assert all(_is_y_monotone(face, mesh.vertices) for face in mesh.faces)


def test_polygon_decomposer_trapezoidal_decomposition_returns_vertical_cells():
    polygon_points = [
        Point(0, 0),
        Point(5, 0),
        Point(5, 5),
        Point(3, 5),
        Point(3, 2),
        Point(2, 2),
        Point(2, 5),
        Point(0, 5),
    ]

    mesh = PolygonDecomposer.trapezoidal_decomposition(polygon_points)

    assert isinstance(mesh, PolygonMesh)
    assert len(mesh.faces) >= 2
    assert all(3 <= len(face) <= 4 for face in mesh.faces)


def test_polygon_decomposer_visibility_decomposition_splits_concave_polygon():
    polygon_points = [Point(0, 0), Point(4, 0), Point(4, 4), Point(2, 2), Point(0, 4)]

    mesh = PolygonDecomposer.visibility_decomposition(polygon_points)

    assert isinstance(mesh, PolygonMesh)
    assert len(mesh.faces) >= 2
    assert all(len(face) >= 3 for face in mesh.faces)
