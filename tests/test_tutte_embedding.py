"""Tests for Tutte Embedding with Cotangent Weights."""

import numpy as np
import pytest


def test_tutte_embedding_import():
    from compgeom.mesh.surface.tutte_embedding import (
        TutteEmbedding,
        CotangentLaplacian,
        tutte_embedding,
        cotangent_laplacian,
    )

    assert TutteEmbedding is not None
    assert CotangentLaplacian is not None


def test_mesh_init_import_from_main():
    from compgeom.mesh import (
        TutteEmbedding,
        CotangentLaplacian,
        tutte_embedding,
        cotangent_laplacian,
    )

    assert TutteEmbedding is not None
    assert CotangentLaplacian is not None


def test_tutte_embedding_init():
    from compgeom.mesh.surface.trimesh.trimesh import TriMesh
    from compgeom.mesh.surface.tutte_embedding import TutteEmbedding
    from compgeom.kernel import Point3D

    nodes = [
        Point3D(0.0, 0.0, 0.0),
        Point3D(1.0, 0.0, 0.0),
        Point3D(1.0, 1.0, 0.0),
        Point3D(0.0, 1.0, 0.0),
    ]
    faces = [(0, 1, 2), (0, 2, 3)]

    mesh = TriMesh(nodes=nodes, faces=faces)
    solver = TutteEmbedding(mesh)

    assert solver.num_v == 4
    assert solver.num_f == 2
    assert len(solver.edges) > 0


def test_tutte_embedding_adjacency():
    from compgeom.mesh.surface.trimesh.trimesh import TriMesh
    from compgeom.mesh.surface.tutte_embedding import TutteEmbedding
    from compgeom.kernel import Point3D

    nodes = [
        Point3D(0.0, 0.0, 0.0),
        Point3D(1.0, 0.0, 0.0),
        Point3D(1.0, 1.0, 0.0),
        Point3D(0.0, 1.0, 0.0),
    ]
    faces = [(0, 1, 2), (0, 2, 3)]

    mesh = TriMesh(nodes=nodes, faces=faces)
    solver = TutteEmbedding(mesh)

    assert 0 in solver.adj[1]
    assert 1 in solver.adj[0]


def test_tutte_embedding_circle():
    from compgeom.mesh.surface.trimesh.trimesh import TriMesh
    from compgeom.mesh.surface.tutte_embedding import TutteEmbedding
    from compgeom.kernel import Point3D

    nodes = [
        Point3D(0.0, 0.0, 0.0),
        Point3D(1.0, 0.0, 0.0),
        Point3D(1.0, 1.0, 0.0),
        Point3D(0.0, 1.0, 0.0),
    ]
    faces = [(0, 1, 2), (0, 2, 3)]

    mesh = TriMesh(nodes=nodes, faces=faces)
    solver = TutteEmbedding(mesh)

    u, v = solver.compute_embedding(boundary_type="circle")
    assert len(u) == 4
    assert len(v) == 4


def test_tutte_embedding_square():
    from compgeom.mesh.surface.trimesh.trimesh import TriMesh
    from compgeom.mesh.surface.tutte_embedding import TutteEmbedding
    from compgeom.kernel import Point3D

    nodes = [
        Point3D(0.0, 0.0, 0.0),
        Point3D(1.0, 0.0, 0.0),
        Point3D(1.0, 1.0, 0.0),
        Point3D(0.0, 1.0, 0.0),
    ]
    faces = [(0, 1, 2), (0, 2, 3)]

    mesh = TriMesh(nodes=nodes, faces=faces)
    solver = TutteEmbedding(mesh)

    u, v = solver.compute_embedding(boundary_type="square")
    assert len(u) == 4
    assert len(v) == 4


def test_cotangent_laplacian():
    from compgeom.mesh.surface.trimesh.trimesh import TriMesh
    from compgeom.mesh.surface.tutte_embedding import CotangentLaplacian
    from compgeom.kernel import Point3D

    nodes = [
        Point3D(0.0, 0.0, 0.0),
        Point3D(1.0, 0.0, 0.0),
        Point3D(1.0, 1.0, 0.0),
        Point3D(0.0, 1.0, 0.0),
    ]
    faces = [(0, 1, 2), (0, 2, 3)]

    mesh = TriMesh(nodes=nodes, faces=faces)
    L = CotangentLaplacian(mesh)

    assert L.L is not None
    assert L.L.shape == (4, 4)


def test_cotangent_laplacian_apply():
    from compgeom.mesh.surface.trimesh.trimesh import TriMesh
    from compgeom.mesh.surface.tutte_embedding import CotangentLaplacian
    from compgeom.kernel import Point3D

    nodes = [
        Point3D(0.0, 0.0, 0.0),
        Point3D(1.0, 0.0, 0.0),
        Point3D(1.0, 1.0, 0.0),
        Point3D(0.0, 1.0, 0.0),
    ]
    faces = [(0, 1, 2), (0, 2, 3)]

    mesh = TriMesh(nodes=nodes, faces=faces)
    L = CotangentLaplacian(mesh)

    u = np.array([1.0, 2.0, 3.0, 4.0])
    Lu = L.apply(u)

    assert len(Lu) == 4


def test_tutte_convenience_function():
    from compgeom.mesh.surface.trimesh.trimesh import TriMesh
    from compgeom.mesh.surface.tutte_embedding import tutte_embedding
    from compgeom.kernel import Point3D

    nodes = [
        Point3D(0.0, 0.0, 0.0),
        Point3D(1.0, 0.0, 0.0),
        Point3D(1.0, 1.0, 0.0),
        Point3D(0.0, 1.0, 0.0),
    ]
    faces = [(0, 1, 2), (0, 2, 3)]

    mesh = TriMesh(nodes=nodes, faces=faces)
    uv = tutte_embedding(mesh)

    assert len(uv) == 4
    assert all(isinstance(c, tuple) and len(c) == 2 for c in uv)
