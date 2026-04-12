"""Tests for ARAP (As-Rigid-As-Possible) mapping."""

import numpy as np
import pytest


def test_arap_mapper_import():
    from compgeom.mesh.surface.arap import ARAPMapper, as_rigid_as_possible

    assert ARAPMapper is not None
    assert as_rigid_as_possible is not None


def test_mesh_init_import_from_main():
    from compgeom.mesh import ARAPMapper, as_rigid_as_possible

    assert ARAPMapper is not None
    assert as_rigid_as_possible is not None


def test_arap_simple_deform():
    from compgeom.mesh.surface.trimesh.trimesh import TriMesh
    from compgeom.mesh.surface.arap import ARAPMapper
    from compgeom.kernel import Point3D

    nodes = [
        Point3D(0.0, 0.0, 0.0),
        Point3D(1.0, 0.0, 0.0),
        Point3D(1.0, 1.0, 0.0),
        Point3D(0.0, 1.0, 0.0),
    ]
    faces = [(0, 1, 2), (0, 2, 3)]

    mesh = TriMesh(nodes=nodes, faces=faces)

    mapper = ARAPMapper(mesh)
    assert mapper.num_v == 4
    assert mapper.num_f == 2
    np.testing.assert_array_almost_equal(mapper.original_vertices[0], [0, 0, 0])


def test_arap_adjacency():
    from compgeom.mesh.surface.trimesh.trimesh import TriMesh
    from compgeom.mesh.surface.arap import ARAPMapper
    from compgeom.kernel import Point3D

    nodes = [
        Point3D(0.0, 0.0, 0.0),
        Point3D(1.0, 0.0, 0.0),
        Point3D(1.0, 1.0, 0.0),
        Point3D(0.0, 1.0, 0.0),
    ]
    faces = [(0, 1, 2), (0, 2, 3)]

    mesh = TriMesh(nodes=nodes, faces=faces)
    mapper = ARAPMapper(mesh)

    assert 0 in mapper.adj[1]
    assert 1 in mapper.adj[0]


def test_arap_parameterize():
    from compgeom.mesh.surface.trimesh.trimesh import TriMesh
    from compgeom.mesh.surface.arap import ARAPMapper
    from compgeom.kernel import Point3D

    nodes = [
        Point3D(0.0, 0.0, 0.0),
        Point3D(1.0, 0.0, 0.0),
        Point3D(1.0, 1.0, 0.0),
        Point3D(0.0, 1.0, 0.0),
    ]
    faces = [(0, 1, 2), (0, 2, 3)]

    mesh = TriMesh(nodes=nodes, faces=faces)
    mapper = ARAPMapper(mesh)

    uv = mapper.parameterize(iterations=5)
    assert len(uv) == 4
    assert all(isinstance(c, tuple) and len(c) == 2 for c in uv)


def test_arap_handle_deformation():
    from compgeom.mesh.surface.trimesh.trimesh import TriMesh
    from compgeom.mesh.surface.arap import ARAPMapper
    from compgeom.kernel import Point3D

    nodes = [
        Point3D(0.0, 0.0, 0.0),
        Point3D(1.0, 0.0, 0.0),
        Point3D(1.0, 1.0, 0.0),
        Point3D(0.0, 1.0, 0.0),
    ]
    faces = [(0, 1, 2), (0, 2, 3)]

    mesh = TriMesh(nodes=nodes, faces=faces)
    mapper = ARAPMapper(mesh)

    handle_vertices = [0]
    handle_positions = [np.array([0.0, 0.0, 0.0])]

    deformed = mapper.deform(
        iterations=3, handle_vertices=handle_vertices, handle_positions=handle_positions
    )

    assert len(deformed) == 4
    assert all(isinstance(v, np.ndarray) and v.shape == (3,) for v in deformed)
