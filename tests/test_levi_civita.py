"""Tests for Levi-Civita Connection."""

import numpy as np
import pytest


def test_levi_civita_import():
    from compgeom.mesh.surface.levi_civita_connection import (
        LeviCivitaConnection,
        SpinConnection,
        parallel_transport,
    )

    assert LeviCivitaConnection is not None
    assert SpinConnection is not None


def test_mesh_init_import_from_main():
    from compgeom.mesh import (
        LeviCivitaConnection,
        parallel_transport,
    )

    assert LeviCivitaConnection is not None
    assert parallel_transport is not None


def test_levi_civita_init():
    from compgeom.mesh.surface.trimesh.trimesh import TriMesh
    from compgeom.mesh.surface.levi_civita_connection import LeviCivitaConnection
    from compgeom.kernel import Point3D

    nodes = [
        Point3D(0.0, 0.0, 0.0),
        Point3D(1.0, 0.0, 0.0),
        Point3D(1.0, 1.0, 0.0),
        Point3D(0.0, 1.0, 0.0),
    ]
    faces = [(0, 1, 2), (0, 2, 3)]

    mesh = TriMesh(nodes=nodes, faces=faces)
    conn = LeviCivitaConnection(mesh)

    assert conn.num_v == 4
    assert conn.num_f == 2


def test_levi_civita_adjacency():
    from compgeom.mesh.surface.trimesh.trimesh import TriMesh
    from compgeom.mesh.surface.levi_civita_connection import LeviCivitaConnection
    from compgeom.kernel import Point3D

    nodes = [
        Point3D(0.0, 0.0, 0.0),
        Point3D(1.0, 0.0, 0.0),
        Point3D(1.0, 1.0, 0.0),
        Point3D(0.0, 1.0, 0.0),
    ]
    faces = [(0, 1, 2), (0, 2, 3)]

    mesh = TriMesh(nodes=nodes, faces=faces)
    conn = LeviCivitaConnection(mesh)

    assert 0 in conn.adj[1]
    assert 1 in conn.adj[0]


def test_levi_civita_transport():
    from compgeom.mesh.surface.trimesh.trimesh import TriMesh
    from compgeom.mesh.surface.levi_civita_connection import LeviCivitaConnection
    from compgeom.kernel import Point3D

    nodes = [
        Point3D(0.0, 0.0, 0.0),
        Point3D(1.0, 0.0, 0.0),
        Point3D(1.0, 1.0, 0.0),
        Point3D(0.0, 1.0, 0.0),
    ]
    faces = [(0, 1, 2), (0, 2, 3)]

    mesh = TriMesh(nodes=nodes, faces=faces)
    conn = LeviCivitaConnection(mesh)

    direction = np.array([1.0, 0.0, 0.0])
    result = conn.compute_transport(0, direction, 2)

    assert result.shape == (3,)
    assert not np.isnan(result).any()


def test_spin_connection():
    from compgeom.mesh.surface.trimesh.trimesh import TriMesh
    from compgeom.mesh.surface.levi_civita_connection import SpinConnection
    from compgeom.kernel import Point3D

    nodes = [
        Point3D(0.0, 0.0, 0.0),
        Point3D(1.0, 0.0, 0.0),
        Point3D(1.0, 1.0, 0.0),
        Point3D(0.0, 1.0, 0.0),
    ]
    faces = [(0, 1, 2), (0, 2, 3)]

    mesh = TriMesh(nodes=nodes, faces=faces)
    conn = SpinConnection(mesh)

    assert conn is not None
    assert conn.connection is not None


def test_parallel_transport_convenience():
    from compgeom.mesh.surface.trimesh.trimesh import TriMesh
    from compgeom.mesh.surface.levi_civita_connection import parallel_transport
    from compgeom.kernel import Point3D

    nodes = [
        Point3D(0.0, 0.0, 0.0),
        Point3D(1.0, 0.0, 0.0),
        Point3D(1.0, 1.0, 0.0),
        Point3D(0.0, 1.0, 0.0),
    ]
    faces = [(0, 1, 2), (0, 2, 3)]

    mesh = TriMesh(nodes=nodes, faces=faces)
    result = parallel_transport(mesh, 0, [1.0, 0.0, 0.0], 2)

    assert len(result) == 3
    assert not np.isnan(result).any()
