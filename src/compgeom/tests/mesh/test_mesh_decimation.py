from compgeom.kernel import Point3D
from compgeom.mesh import MeshDecimator, TriMesh


def test_decimate_returns_input_mesh_when_target_is_not_smaller():
    mesh = TriMesh(
        [
            Point3D(0, 0, 0),
            Point3D(1, 0, 0),
            Point3D(0, 1, 0),
            Point3D(1, 1, 0),
        ],
        [(0, 1, 2), (1, 3, 2)],
    )

    result = MeshDecimator.decimate(mesh, target_faces=2)

    assert result is mesh


def test_decimate_reduces_two_triangle_patch_to_one_triangle():
    mesh = TriMesh(
        [
            Point3D(0, 0, 0),
            Point3D(1, 0, 0),
            Point3D(0, 1, 0),
            Point3D(1, 1, 0),
        ],
        [(0, 1, 2), (1, 3, 2)],
    )

    result = MeshDecimator.decimate(mesh, target_faces=1)

    assert len(result.vertices) == 3
    assert len(result.faces) == 1
    assert result.faces[0] == (0, 2, 1)
    assert all(isinstance(vertex, Point3D) for vertex in result.vertices)
    assert result.bounding_box() == ((0.0, 0.0, 0.0), (1.0, 1.0, 0.0))


def test_decimate_four_triangle_strip_preserves_outer_extent():
    mesh = TriMesh(
        [
            Point3D(0, 0, 0),
            Point3D(1, 0, 0),
            Point3D(2, 0, 0),
            Point3D(0, 1, 0),
            Point3D(1, 1, 0),
            Point3D(2, 1, 0),
        ],
        [(0, 1, 3), (1, 4, 3), (1, 2, 4), (2, 5, 4)],
    )

    result = MeshDecimator.decimate(mesh, target_faces=2)

    assert len(result.vertices) == 4
    assert len(result.faces) == 2
    assert result.bounding_box() == ((0.5, 0.0, 0.0), (2.0, 1.0, 0.0))
    assert set(result.faces) == {(0, 1, 2), (1, 3, 2)}
