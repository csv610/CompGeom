import pytest

from compgeom.kernel import Point3D
from compgeom.mesh import TriangleMesh
from compgeom.mesh.surfmesh.mesh_processing import MeshProcessing
from compgeom.mesh.surfmesh.remesher import AdaptiveRemesher
from compgeom.mesh.surfmesh.surf_mesh_repair import SurfMeshRepair


def make_open_patch():
    return TriangleMesh(
        [
            Point3D(0, 0, 0),
            Point3D(1, 0, 0),
            Point3D(1, 1, 0),
            Point3D(0, 1, 0),
        ],
        [(0, 1, 2), (0, 2, 3)],
    )


def make_pyramid_patch():
    return TriangleMesh(
        [
            Point3D(0, 0, 0),
            Point3D(2, 0, 0),
            Point3D(2, 2, 0),
            Point3D(0, 2, 0),
            Point3D(1, 1, 1),
        ],
        [(0, 1, 4), (1, 2, 4), (2, 3, 4), (3, 0, 4)],
    )


def test_laplacian_smoothing_moves_only_the_interior_vertex():
    mesh = make_pyramid_patch()

    smoothed = MeshProcessing.laplacian_smoothing(mesh, iterations=1, lambda_factor=0.5)

    assert (smoothed.vertices[0].x, smoothed.vertices[0].y, smoothed.vertices[0].z) == (0, 0, 0)
    assert (smoothed.vertices[4].x, smoothed.vertices[4].y, smoothed.vertices[4].z) == pytest.approx((1.0, 1.0, 0.5))


def test_fill_holes_currently_returns_none():
    assert MeshProcessing.fill_holes(make_open_patch()) is None


def test_bilateral_and_taubin_smoothing_preserve_basic_mesh_structure():
    mesh = make_pyramid_patch()

    bilateral = MeshProcessing.bilateral_smoothing(mesh, iterations=1)
    taubin = MeshProcessing.taubin_smoothing(make_open_patch(), iterations=1)

    assert bilateral.faces == mesh.faces
    assert bilateral.vertices[4].z == pytest.approx(1.0)
    assert taubin.faces == make_open_patch().faces


def test_loop_subdivision_currently_returns_none():
    assert MeshProcessing.loop_subdivision(make_open_patch(), iterations=1) is None


def test_mesh_offset_returns_offset_shell_and_create_solid_is_unfinished():
    mesh = make_open_patch()

    offset = MeshProcessing.mesh_offset(mesh, 1.0, create_solid=False)

    assert len(offset.vertices) == len(mesh.vertices)
    assert offset.faces == mesh.faces
    assert all(vertex.z == pytest.approx(1.0) for vertex in offset.vertices)
    assert MeshProcessing.mesh_offset(mesh, 1.0, create_solid=True) is None


def test_mesh_clipping_currently_raises_name_error_for_missing_math_import():
    with pytest.raises(NameError):
        MeshProcessing.mesh_clipping(make_pyramid_patch(), (0, 0, 0.5), (0, 0, 1))


def test_catmull_clark_returns_input_mesh():
    mesh = make_open_patch()

    assert MeshProcessing.catmull_clark(mesh, iterations=2) is mesh


def test_repair_duplicate_and_degenerate_cleanup_helpers():
    mesh = TriangleMesh(
        [
            Point3D(0, 0, 0),
            Point3D(0, 0, 0),
            Point3D(1, 0, 0),
            Point3D(0, 1, 0),
        ],
        [(0, 2, 3), (1, 2, 3), (0, 0, 2)],
    )

    deduped = SurfMeshRepair.remove_duplicate_points(mesh)
    degen_removed = SurfMeshRepair.remove_degenerate_faces(mesh)

    assert deduped.faces == [(0, 1, 2), (0, 1, 2)]
    assert degen_removed.faces == [(0, 2, 3), (1, 2, 3)]


def test_repair_duplicate_faces_and_fix_normals():
    mesh = TriangleMesh(
        [
            Point3D(0, 0, 0),
            Point3D(1, 0, 0),
            Point3D(0, 1, 0),
            Point3D(1, 1, 0),
        ],
        [(0, 1, 2), (2, 1, 0), (1, 2, 3)],
    )

    unique = SurfMeshRepair.remove_duplicate_faces(mesh)
    fixed = SurfMeshRepair.fix_normals(TriangleMesh(mesh.vertices, [(0, 1, 2), (1, 2, 3)]))

    assert unique.faces == [(0, 1, 2), (1, 2, 3)]
    assert fixed.faces == [(0, 1, 2), (2, 1, 3)]


def test_repair_non_manifold_and_isolated_vertex_helpers():
    non_manifold_faces = TriangleMesh(
        [
            Point3D(0, 0, 0),
            Point3D(1, 0, 0),
            Point3D(0, 1, 0),
            Point3D(0, 0, 1),
            Point3D(0, -1, 0),
        ],
        [(0, 1, 2), (0, 1, 3), (0, 1, 4)],
    )
    non_manifold_vertex = TriangleMesh(
        [
            Point3D(0, 0, 0),
            Point3D(1, 0, 0),
            Point3D(0, 1, 0),
            Point3D(2, 0, 0),
            Point3D(2, 1, 0),
            Point3D(3, 0, 0),
            Point3D(3, 1, 0),
        ],
        [(0, 1, 2), (1, 3, 4), (1, 5, 6)],
    )
    isolated = TriangleMesh(
        [Point3D(0, 0, 0), Point3D(1, 0, 0), Point3D(0, 1, 0), Point3D(5, 5, 5)],
        [(0, 1, 2)],
    )

    assert SurfMeshRepair.remove_non_manifold_faces(non_manifold_faces).faces == []
    assert SurfMeshRepair.remove_non_manifold_vertices(non_manifold_vertex).faces == [(0, 1, 2)]
    assert len(SurfMeshRepair.remove_isolated_vertices(isolated).vertices) == 3


def test_repair_self_intersection_component_filtering_and_pipeline():
    crossing = TriangleMesh(
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
    components = TriangleMesh(
        [
            Point3D(0, 0, 0),
            Point3D(1, 0, 0),
            Point3D(0, 1, 0),
            Point3D(1, 1, 0),
            Point3D(2, 0, 0),
            Point3D(2, 1, 0),
            Point3D(10, 0, 0),
            Point3D(11, 0, 0),
            Point3D(10, 1, 0),
        ],
        [(0, 1, 2), (1, 3, 2), (1, 4, 3), (6, 7, 8)],
    )
    noisy = TriangleMesh(
        [
            Point3D(0, 0, 0),
            Point3D(0, 0, 0),
            Point3D(1, 0, 0),
            Point3D(0, 1, 0),
            Point3D(5, 5, 5),
        ],
        [(0, 2, 3), (1, 2, 3)],
    )

    assert SurfMeshRepair.remove_self_intersections(crossing).faces == [(0, 1, 2)]
    assert SurfMeshRepair.remove_small_components(components, min_fraction=0.8).faces == [
        (0, 1, 2),
        (1, 3, 2),
        (1, 4, 3),
    ]
    repaired = SurfMeshRepair.repair(noisy)
    assert len(repaired.vertices) == 3
    assert repaired.faces == [(0, 1, 2)]


def test_adaptive_remesher_helpers_follow_current_placeholder_behavior():
    mesh = make_open_patch()

    collapsed = AdaptiveRemesher._adaptive_collapse(mesh, [0.5] * len(mesh.vertices))
    remeshed = AdaptiveRemesher.remesh(mesh, min_edge=0.1, max_edge=1.0, iterations=1)

    assert collapsed is mesh
    assert len(remeshed.vertices) == 5
    assert len(remeshed.faces) == 3
