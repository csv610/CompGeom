import math

import pytest

from compgeom.kernel import Point3D
from compgeom.mesh import TriMesh
from compgeom.mesh.surface.bounding_volumes import BoundingVolumes
from compgeom.mesh.surface.curvature import MeshCurvature
from compgeom.mesh.surface.mesh_analysis import MeshAnalysis
from compgeom.mesh.surface.mesh_quality import MeshQuality


def make_triangle():
    return TriMesh(
        [Point3D(0, 0, 0), Point3D(1, 0, 0), Point3D(0, 1, 0)],
        [(0, 1, 2)],
    )


def make_tetra_surface():
    return TriMesh(
        [
            Point3D(0, 0, 0),
            Point3D(1, 0, 0),
            Point3D(0, 1, 0),
            Point3D(0, 0, 1),
        ],
        [(0, 1, 2), (0, 1, 3), (0, 2, 3), (1, 2, 3)],
    )


def make_annulus():
    return TriMesh(
        [
            Point3D(0, 0, 0),
            Point3D(3, 0, 0),
            Point3D(3, 3, 0),
            Point3D(0, 3, 0),
            Point3D(1, 1, 0),
            Point3D(2, 1, 0),
            Point3D(2, 2, 0),
            Point3D(1, 2, 0),
        ],
        [
            (0, 1, 5), (0, 5, 4),
            (1, 2, 6), (1, 6, 5),
            (2, 3, 7), (2, 7, 6),
            (3, 0, 4), (3, 4, 7),
        ],
    )


def test_mesh_quality_metrics_for_right_triangle():
    mesh = make_triangle()

    aspect_ratio = MeshQuality.aspect_ratio(mesh)
    min_max_angles = MeshQuality.min_max_angles(mesh)

    assert aspect_ratio == [pytest.approx(1.2071067811865483)]
    assert min_max_angles == [(pytest.approx(45.0), pytest.approx(90.0))]


def test_face_and_vertex_normals_for_planar_triangle():
    mesh = make_triangle()

    face_normals = MeshAnalysis.compute_face_normals(mesh)
    vertex_normals = MeshAnalysis.compute_vertex_normals(mesh)

    assert face_normals == [(0.0, 0.0, 1.0)]
    assert vertex_normals == [(0.0, 0.0, 1.0)] * 3


def test_total_area_volume_and_center_of_mass_for_tetra_surface():
    mesh = make_tetra_surface()

    assert MeshAnalysis.total_area(mesh) == pytest.approx(2.3660254037844384)
    assert MeshAnalysis.total_volume(mesh) == pytest.approx(1.0 / 6.0)
    assert MeshAnalysis.center_of_mass(mesh) == pytest.approx((0.25, 0.25, 0.25))


def test_inertia_tensor_currently_returns_none():
    mesh = make_tetra_surface()

    assert MeshAnalysis.inertia_tensor(mesh) is None


def test_generate_report_contains_topology_and_mass_properties():
    mesh = make_tetra_surface()

    report = MeshAnalysis.generate_report(mesh)

    assert "Vertices: 4" in report
    assert "Faces:    4" in report
    assert "Euler Characteristic: 2" in report
    assert "Betti Numbers: b0=1, b1=0, b2=1" in report
    assert "Watertight: Yes" in report
    assert "Center of Mass: (0.2500, 0.2500, 0.2500)" in report


def test_betti_numbers_for_open_closed_disconnected_and_holed_meshes():
    triangle = make_triangle()
    tetra = make_tetra_surface()
    annulus = make_annulus()
    disconnected = TriMesh(
        tetra.vertices + [Point3D(p.x + 3.0, p.y, p.z) for p in tetra.vertices],
        [face.v_indices for face in tetra.faces]
        + [tuple(index + 4 for index in face.v_indices) for face in tetra.faces],
    )

    assert triangle.betti_numbers() == (1, 0, 0)
    assert tetra.betti_numbers() == (1, 0, 1)
    assert annulus.betti_numbers() == (1, 1, 0)
    assert disconnected.betti_numbers() == (2, 0, 2)


def test_curvature_methods_return_per_vertex_values():
    mesh = make_triangle()

    gaussian = MeshCurvature.gaussian_curvature(mesh)
    mean = MeshCurvature.mean_curvature(mesh)

    assert len(gaussian) == len(mesh.vertices)
    assert len(mean) == len(mesh.vertices)
    assert gaussian[0] == pytest.approx(28.274333882308138)
    assert mean == pytest.approx([0.0, 0.5, 0.5])


def test_compute_obb_points_returns_right_handed_orthonormal_axes():
    points = [
        Point3D(0, 0, 0),
        Point3D(1, 0, 0),
        Point3D(0, 1, 0),
        Point3D(0, 0, 1),
    ]

    center, axes, extents = BoundingVolumes.compute_obb_points(points)

    assert (center.x, center.y, center.z) == pytest.approx(
        (0.08333333333333326, 0.08333333333333359, 0.33333333333333337)
    )
    for extent in extents:
        assert extent > 0
    for axis in axes:
        assert math.sqrt(sum(component * component for component in axis)) == pytest.approx(1.0)
    assert sum(axes[0][i] * axes[1][i] for i in range(3)) == pytest.approx(0.0, abs=1e-8)
    assert sum(axes[1][i] * axes[2][i] for i in range(3)) == pytest.approx(0.0, abs=1e-8)
    assert sum(axes[0][i] * axes[2][i] for i in range(3)) == pytest.approx(0.0, abs=1e-8)


def test_compute_min_sphere_and_min_ellipse_for_tetra_points():
    points = [
        Point3D(0, 0, 0),
        Point3D(1, 0, 0),
        Point3D(0, 1, 0),
        Point3D(0, 0, 1),
    ]

    sphere_center, radius = BoundingVolumes.compute_min_sphere(points)
    ellipse_center, axes = BoundingVolumes.compute_min_ellipse(points)

    assert (sphere_center.x, sphere_center.y, sphere_center.z) == pytest.approx(
        (1.0 / 3.0, 1.0 / 3.0, 1.0 / 3.0)
    )
    assert radius == pytest.approx(0.816496580927726)
    assert (ellipse_center.x, ellipse_center.y, ellipse_center.z) == pytest.approx(
        (0.25, 0.25, 0.25)
    )
    assert len(axes) == 3
    assert all(len(axis) == 3 for axis in axes)


def test_pca_align_recenters_mesh_around_origin():
    mesh = TriMesh(
        [
            Point3D(0, 0, 0),
            Point3D(1, 0, 0),
            Point3D(1, 1, 0),
            Point3D(0, 1, 0),
        ],
        [(0, 1, 2), (0, 2, 3)],
    )

    aligned = BoundingVolumes.pca_align(mesh)

    bbox_min, bbox_max = aligned.bounding_box()
    assert bbox_min == pytest.approx((-0.5, -0.5, 0.0))
    assert bbox_max == pytest.approx((0.5, 0.5, 0.0))
