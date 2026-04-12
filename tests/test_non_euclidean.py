"""Tests for Non-Euclidean Geometry."""

import numpy as np
import pytest


def test_non_euclidean_import():
    from compgeom.mesh.surface.non_euclidean import (
        SphericalConformalMap,
        PoincareDiskEmbedding,
        stereographic_forward,
        stereographic_inverse,
        poincare_disk_embedding,
        hyperbolic_distance,
        hemisphere_embedding,
    )

    assert SphericalConformalMap is not None
    assert stereographic_forward is not None


def test_mesh_init_import_from_main():
    from compgeom.mesh import (
        SphericalConformalMap,
        poincare_disk_map,
    )

    assert SphericalConformalMap is not None
    assert poincare_disk_map is not None


def test_stereographic_forward():
    from compgeom.mesh.surface.non_euclidean import stereographic_forward

    points = [(0.0, 0.0), (1.0, 0.0), (0.0, 1.0)]
    sphere_pts = stereographic_forward(points)

    assert sphere_pts.shape == (3, 3)
    norms = np.linalg.norm(sphere_pts, axis=1)
    np.testing.assert_allclose(norms, np.ones(3), rtol=1e-5)


def test_stereographic_roundtrip():
    from compgeom.mesh.surface.non_euclidean import (
        stereographic_forward,
        stereographic_inverse,
    )

    points = [(0.0, 0.0), (0.5, 0.5), (1.0, 0.0)]
    sphere_pts = stereographic_forward(points)
    planar_pts = stereographic_inverse(sphere_pts)

    assert len(planar_pts) == 3


def test_poincare_disk():
    from compgeom.mesh.surface.non_euclidean import poincare_disk_embedding

    points = np.array(
        [
            [0.0, 0.0, 0.0],
            [1.0, 0.0, 0.0],
            [1.0, 1.0, 0.0],
        ]
    )
    disk = poincare_disk_embedding(points)

    assert disk.shape[1] == 2
    assert np.all(disk[:, 0] ** 2 + disk[:, 1] ** 2 <= 1.0 + 1e-5)


def test_hyperbolic_distance():
    from compgeom.mesh.surface.non_euclidean import hyperbolic_distance

    p1 = np.array([0.0, 0.0])
    p2 = np.array([0.5, 0.0])

    dist = hyperbolic_distance(p1, p2)
    assert dist > 0


def test_hemisphere():
    from compgeom.mesh.surface.non_euclidean import hemisphere_embedding

    points = np.array(
        [
            [1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0],
            [0.0, 0.0, 1.0],
        ]
    )
    hemisphere = hemisphere_embedding(points)

    assert hemisphere.shape == (3, 3)
    norms = np.linalg.norm(hemisphere, axis=1)
    np.testing.assert_allclose(norms, np.ones(3), rtol=1e-5)
    assert np.all(hemisphere[:, 2] >= -1e-5)


def test_spherical_conformal_map():
    from compgeom.mesh.surface.trimesh.trimesh import TriMesh
    from compgeom.mesh.surface.non_euclidean import SphericalConformalMap
    from compgeom.kernel import Point3D

    nodes = [
        Point3D(0.0, 0.0, 0.0),
        Point3D(1.0, 0.0, 0.0),
        Point3D(1.0, 1.0, 0.0),
        Point3D(0.0, 1.0, 0.0),
    ]
    faces = [(0, 1, 2), (0, 2, 3)]

    mesh = TriMesh(nodes=nodes, faces=faces)
    mapper = SphericalConformalMap(mesh)

    sphere_pts = mapper.compute_spherical_map()

    assert sphere_pts.shape == (4, 3)
    norms = np.linalg.norm(sphere_pts, axis=1)
    np.testing.assert_allclose(norms, np.ones(4), rtol=1e-5)


def test_poincare_disk_convenience():
    from compgeom.mesh.surface.trimesh.trimesh import TriMesh
    from compgeom.mesh.surface.non_euclidean import poincare_disk_map
    from compgeom.kernel import Point3D

    nodes = [
        Point3D(0.0, 0.0, 0.0),
        Point3D(1.0, 0.0, 0.0),
        Point3D(1.0, 1.0, 0.0),
        Point3D(0.0, 1.0, 0.0),
    ]
    faces = [(0, 1, 2), (0, 2, 3)]

    mesh = TriMesh(nodes=nodes, faces=faces)
    coords = poincare_disk_map(mesh)

    assert len(coords) == 4
    assert all(isinstance(c, tuple) and len(c) == 2 for c in coords)
