import pytest

from compgeom.kernel import Point3D
from compgeom.mesh import TriMesh
from compgeom.mesh.surfmesh.halfedge_mesh import HalfEdgeMesh
from compgeom.mesh.surfmesh.mesh_queries import MeshQueries
from compgeom.mesh.surfmesh.mesh_validation import MeshValidation
from compgeom.mesh.surfmesh.spatial_acceleration import AABBTree


def make_patch():
    return TriMesh(
        [
            Point3D(0, 0, 0),
            Point3D(1, 0, 0),
            Point3D(1, 1, 0),
            Point3D(0, 1, 0),
        ],
        [(0, 1, 2), (0, 2, 3)],
    )


def make_crossing_triangles():
    return TriMesh(
        [
            Point3D(0, 0, 0),
            Point3D(2, 0, 0),
            Point3D(1, 2, 0),
            Point3D(0, 1.5, 0),
            Point3D(2, 1.5, 0),
            Point3D(1, -0.5, 0),
        ],
        [(0, 1, 2), (3, 4, 5)],
    )


def test_halfedge_round_trip_preserves_faces_and_counts():
    mesh = make_patch()

    he_mesh = HalfEdgeMesh.from_triangle_mesh(mesh)
    round_trip = he_mesh.to_triangle_mesh()

    assert len(he_mesh.vertices) == 4
    assert len(he_mesh.faces) == 2
    assert len(he_mesh.edges) == 6
    assert round_trip.faces == mesh.faces


def test_halfedge_assigns_twins_on_shared_edge_only():
    he_mesh = HalfEdgeMesh.from_triangle_mesh(make_patch())

    twin_pairs = sum(1 for edge in he_mesh.edges if edge.twin is not None)

    assert twin_pairs == 2
    assert he_mesh.vertex_neighbors(0) == {1, 2}
    assert he_mesh.vertex_neighbors(2) == {3}


def test_single_ray_triangle_intersection_and_distance_helpers():
    mesh = TriMesh(
        [Point3D(0, 0, 0), Point3D(1, 0, 0), Point3D(0, 1, 0)],
        [(0, 1, 2)],
    )

    distance = MeshQueries._single_ray_tri_intersect(mesh, 0, (0.2, 0.2, 1.0), (0.0, 0.0, -1.0))
    distance_sq = MeshQueries._point_triangle_dist_sq(
        (0.2, 0.2, 1.0),
        (0.0, 0.0, 0.0),
        (1.0, 0.0, 0.0),
        (0.0, 1.0, 0.0),
    )

    assert distance == pytest.approx(1.0)
    assert distance_sq == pytest.approx(1.0)


def test_ray_intersect_matches_between_bruteforce_and_spatial_tree():
    mesh = TriMesh(
        [Point3D(0, 0, 0), Point3D(1, 0, 0), Point3D(0, 1, 0)],
        [(0, 1, 2)],
    )

    brute_force = MeshQueries.ray_intersect(mesh, (0.2, 0.2, 1.0), (0.0, 0.0, -1.0), use_spatial=False)
    spatial = MeshQueries.ray_intersect(mesh, (0.2, 0.2, 1.0), (0.0, 0.0, -1.0), use_spatial=True)

    assert brute_force == [(0, pytest.approx(1.0))]
    assert spatial == brute_force


def test_compute_sdf_and_slice_mesh_currently_return_none():
    mesh = TriMesh(
        [Point3D(0, 0, 0), Point3D(1, 0, 0), Point3D(0, 1, 0)],
        [(0, 1, 2)],
    )

    assert MeshQueries.compute_sdf(mesh, (0.2, 0.2, 1.0), use_spatial=False) is None
    assert MeshQueries.slice_mesh(mesh, (0.0, 0.0, 0.0), (0.0, 0.0, 1.0)) is None


def test_mesh_intersection_and_self_intersection_detection_on_crossing_faces():
    mesh = make_crossing_triangles()

    intersections = MeshQueries.mesh_intersection(mesh, mesh)

    assert (0, 1) in intersections
    assert (1, 0) in intersections
    assert MeshValidation.has_self_intersections(mesh) is True


def test_generalized_winding_number_currently_raises_name_error():
    mesh = TriMesh(
        [
            Point3D(0, 0, 0),
            Point3D(1, 0, 0),
            Point3D(0, 1, 0),
            Point3D(0, 0, 1),
        ],
        [(0, 1, 2), (0, 1, 3), (0, 2, 3), (1, 2, 3)],
    )

    with pytest.raises(NameError):
        MeshQueries.generalized_winding_number(mesh, (0.1, 0.1, 0.1))


def test_aabb_tree_builds_and_reports_sorted_intersections():
    mesh = make_patch()

    tree = AABBTree(mesh, max_faces_per_leaf=1)
    hits = tree.ray_intersect((0.25, 0.25, 1.0), (0.0, 0.0, -1.0))

    assert tree.root is not None
    assert tree.root.is_leaf() is False
    assert hits[0][1] == pytest.approx(1.0)


def test_mesh_validation_report_for_open_patch():
    mesh = make_patch()

    report = MeshValidation.validate(mesh)

    assert MeshValidation.is_manifold(mesh) is True
    assert report == {
        "no_degenerate_faces": True,
        "is_edge_manifold": True,
        "is_watertight": False,
        "is_orientable": True,
        "consistent_normals": True,
        "no_self_intersections": True,
    }
