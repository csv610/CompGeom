"""Tests for Mean Value Coordinates."""

import numpy as np
import pytest


def test_mvc_import():
    from compgeom.mesh.surface.mean_value_coordinates import (
        MeanValueCoordinates,
        MeanValueEmbedding,
        MeanValueLaplacian,
        mean_value_coordinates,
    )

    assert MeanValueCoordinates is not None
    assert MeanValueEmbedding is not None


def test_mesh_init_import_from_main():
    from compgeom.mesh import (
        MeanValueCoordinates,
        mean_value_coordinates,
    )

    assert MeanValueCoordinates is not None
    assert mean_value_coordinates is not None


def test_mvc_init():
    from compgeom.mesh.surface.trimesh.trimesh import TriMesh
    from compgeom.mesh.surface.mean_value_coordinates import MeanValueCoordinates
    from compgeom.kernel import Point3D

    nodes = [
        Point3D(0.0, 0.0, 0.0),
        Point3D(1.0, 0.0, 0.0),
        Point3D(1.0, 1.0, 0.0),
        Point3D(0.0, 1.0, 0.0),
    ]
    faces = [(0, 1, 2), (0, 2, 3)]

    mesh = TriMesh(nodes=nodes, faces=faces)
    solver = MeanValueCoordinates(mesh)

    assert solver.num_v == 4
    assert solver.num_f == 2


def test_mvc_adjacency():
    from compgeom.mesh.surface.trimesh.trimesh import TriMesh
    from compgeom.mesh.surface.mean_value_coordinates import MeanValueCoordinates
    from compgeom.kernel import Point3D

    nodes = [
        Point3D(0.0, 0.0, 0.0),
        Point3D(1.0, 0.0, 0.0),
        Point3D(1.0, 1.0, 0.0),
        Point3D(0.0, 1.0, 0.0),
    ]
    faces = [(0, 1, 2), (0, 2, 3)]

    mesh = TriMesh(nodes=nodes, faces=faces)
    solver = MeanValueCoordinates(mesh)

    assert 0 in solver.adj[1]
    assert 1 in solver.adj[0]


def test_mvc_weights():
    from compgeom.mesh.surface.trimesh.trimesh import TriMesh
    from compgeom.mesh.surface.mean_value_coordinates import MeanValueCoordinates
    from compgeom.kernel import Point3D

    nodes = [
        Point3D(0.0, 0.0, 0.0),
        Point3D(1.0, 0.0, 0.0),
        Point3D(1.0, 1.0, 0.0),
        Point3D(0.0, 1.0, 0.0),
    ]
    faces = [(0, 1, 2), (0, 2, 3)]

    mesh = TriMesh(nodes=nodes, faces=faces)
    solver = MeanValueCoordinates(mesh)

    weights = solver.compute_mean_value_weights(0)
    assert len(weights) > 0
    assert all(w > 0 for w in weights.values())


def test_mvc_embedding():
    from compgeom.mesh.surface.trimesh.trimesh import TriMesh
    from compgeom.mesh.surface.mean_value_coordinates import MeanValueCoordinates
    from compgeom.kernel import Point3D

    nodes = [
        Point3D(0.0, 0.0, 0.0),
        Point3D(1.0, 0.0, 0.0),
        Point3D(1.0, 1.0, 0.0),
        Point3D(0.0, 1.0, 0.0),
    ]
    faces = [(0, 1, 2), (0, 2, 3)]

    mesh = TriMesh(nodes=nodes, faces=faces)
    solver = MeanValueCoordinates(mesh)

    u, v = solver.compute_embedding(iterations=10)
    assert len(u) == 4
    assert len(v) == 4


def test_mvc_wrapper():
    from compgeom.mesh.surface.trimesh.trimesh import TriMesh
    from compgeom.mesh.surface.mean_value_coordinates import MeanValueEmbedding
    from compgeom.kernel import Point3D

    nodes = [
        Point3D(0.0, 0.0, 0.0),
        Point3D(1.0, 0.0, 0.0),
        Point3D(1.0, 1.0, 0.0),
        Point3D(0.0, 1.0, 0.0),
    ]
    faces = [(0, 1, 2), (0, 2, 3)]

    mesh = TriMesh(nodes=nodes, faces=faces)
    wrapper = MeanValueEmbedding(mesh)

    uv = wrapper.compute(iterations=5)
    assert len(uv) == 4
    assert all(isinstance(c, tuple) and len(c) == 2 for c in uv)


def test_mvc_laplacian():
    from compgeom.mesh.surface.trimesh.trimesh import TriMesh
    from compgeom.mesh.surface.mean_value_coordinates import MeanValueLaplacian
    from compgeom.kernel import Point3D

    nodes = [
        Point3D(0.0, 0.0, 0.0),
        Point3D(1.0, 0.0, 0.0),
        Point3D(1.0, 1.0, 0.0),
        Point3D(0.0, 1.0, 0.0),
    ]
    faces = [(0, 1, 2), (0, 2, 3)]

    mesh = TriMesh(nodes=nodes, faces=faces)
    L = MeanValueLaplacian(mesh)

    assert L.L is not None
    assert L.L.shape == (4, 4)


def test_mvc_convenience():
    from compgeom.mesh.surface.trimesh.trimesh import TriMesh
    from compgeom.mesh.surface.mean_value_coordinates import mean_value_coordinates
    from compgeom.kernel import Point3D

    nodes = [
        Point3D(0.0, 0.0, 0.0),
        Point3D(1.0, 0.0, 0.0),
        Point3D(1.0, 1.0, 0.0),
        Point3D(0.0, 1.0, 0.0),
    ]
    faces = [(0, 1, 2), (0, 2, 3)]

    mesh = TriMesh(nodes=nodes, faces=faces)
    uv = mean_value_coordinates(mesh, iterations=5)

    assert len(uv) == 4
    assert all(isinstance(c, tuple) and len(c) == 2 for c in uv)
