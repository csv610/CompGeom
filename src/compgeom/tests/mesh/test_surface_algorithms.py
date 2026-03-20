import builtins

import pytest

from compgeom.kernel import Point2D, Point3D
from compgeom.mesh import TriMesh
from compgeom.mesh.surface.alpha_shapes import AlphaShape
from compgeom.mesh.surface.convex_hull import ConvexHull3D
from compgeom.mesh.surface.mesh_booleans import MeshBooleans
from compgeom.mesh.surface.parameterization import MeshParameterization
from compgeom.mesh.surface.registration import MeshRegistration


def block_scipy_imports(monkeypatch):
    original_import = builtins.__import__

    def guarded_import(name, globals=None, locals=None, fromlist=(), level=0):
        if name == "scipy" or name.startswith("scipy."):
            raise ImportError("blocked for test")
        return original_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", guarded_import)


def test_alpha_shape_2d_depends_on_alpha_threshold():
    points = [
        Point2D(0, 0),
        Point2D(2, 0),
        Point2D(2, 2),
        Point2D(0, 2),
        Point2D(1, 1),
    ]

    small_alpha = AlphaShape.compute_2d(points, 1.0)
    larger_alpha = sorted(AlphaShape.compute_2d(points, 2.0))

    assert small_alpha == []
    assert len(larger_alpha) == 4
    assert all(0 <= i <= 4 and 0 <= j <= 4 for i, j in larger_alpha)
    assert any(4 in edge for edge in larger_alpha)


def test_alpha_shape_3d_returns_empty_mesh_for_simple_tetra_case():
    mesh = AlphaShape.compute_3d(
        [
            Point3D(0, 0, 0),
            Point3D(1, 0, 0),
            Point3D(0, 1, 0),
            Point3D(0, 0, 1),
        ],
        2.0,
    )

    assert mesh.vertices == []
    assert mesh.faces == []


@pytest.mark.parametrize("operation", ["union", "intersection", "difference"])
def test_mesh_booleans_currently_fail_because_sdf_returns_none(operation):
    mesh = TriMesh(
        [Point3D(0, 0, 0), Point3D(1, 0, 0), Point3D(0, 1, 0)],
        [(0, 1, 2)],
    )

    with pytest.raises(TypeError):
        getattr(MeshBooleans, operation)(mesh, mesh)


def test_convex_hull_reports_missing_scipy_dependency(monkeypatch):
    block_scipy_imports(monkeypatch)

    with pytest.raises(ImportError, match="requires 'scipy' and 'numpy'"):
        ConvexHull3D.compute(
            [
                Point3D(0, 0, 0),
                Point3D(1, 0, 0),
                Point3D(0, 1, 0),
                Point3D(0, 0, 1),
            ]
        )


def test_harmonic_map_reports_missing_scipy_dependency(monkeypatch):
    block_scipy_imports(monkeypatch)
    mesh = TriMesh(
        [
            Point3D(0, 0, 0),
            Point3D(1, 0, 0),
            Point3D(1, 1, 0),
            Point3D(0, 1, 0),
        ],
        [(0, 1, 2), (0, 2, 3)],
    )

    with pytest.raises(ImportError, match="Harmonic mapping requires 'numpy' and 'scipy'"):
        MeshParameterization.harmonic_map(mesh)


def test_lscm_returns_zero_uvs_for_each_vertex():
    mesh = TriMesh(
        [Point3D(0, 0, 0), Point3D(1, 0, 0), Point3D(0, 1, 0)],
        [(0, 1, 2)],
    )

    uv = MeshParameterization.lscm(mesh)

    assert [(point.x, point.y) for point in uv] == [(0, 0), (0, 0), (0, 0)]


def test_icp_reports_missing_scipy_dependency(monkeypatch):
    block_scipy_imports(monkeypatch)
    source = TriMesh(
        [Point3D(1, 0, 0), Point3D(2, 0, 0), Point3D(1, 1, 0)],
        [(0, 1, 2)],
    )
    target = TriMesh(
        [Point3D(0, 0, 0), Point3D(1, 0, 0), Point3D(0, 1, 0)],
        [(0, 1, 2)],
    )

    with pytest.raises(ImportError, match="ICP requires 'numpy' and 'scipy'"):
        MeshRegistration.icp(source, target)
