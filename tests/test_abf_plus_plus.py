"""Tests for ABF++ Parameterization."""

import numpy as np
import pytest


def test_abf_import():
    from compgeom.mesh.surface.abf_plus_plus import (
        ABFPlusPlus,
        ABFParameterization,
        abf_plus_plus,
    )

    assert ABFPlusPlus is not None
    assert ABFParameterization is not None
    assert abf_plus_plus is not None


def test_mesh_init_import_from_main():
    from compgeom.mesh import (
        ABFPlusPlus,
        abf_plus_plus,
    )

    assert ABFPlusPlus is not None
    assert abf_plus_plus is not None


def test_abf_init():
    from compgeom.mesh.surface.trimesh.trimesh import TriMesh
    from compgeom.mesh.surface.abf_plus_plus import ABFPlusPlus
    from compgeom.kernel import Point3D

    nodes = [
        Point3D(0.0, 0.0, 0.0),
        Point3D(1.0, 0.0, 0.0),
        Point3D(1.0, 1.0, 0.0),
        Point3D(0.0, 1.0, 0.0),
    ]
    faces = [(0, 1, 2), (0, 2, 3)]

    mesh = TriMesh(nodes=nodes, faces=faces)
    solver = ABFPlusPlus(mesh)

    assert solver.num_v == 4
    assert solver.num_f == 2


def test_abf_adjacency():
    from compgeom.mesh.surface.trimesh.trimesh import TriMesh
    from compgeom.mesh.surface.abf_plus_plus import ABFPlusPlus
    from compgeom.kernel import Point3D

    nodes = [
        Point3D(0.0, 0.0, 0.0),
        Point3D(1.0, 0.0, 0.0),
        Point3D(1.0, 1.0, 0.0),
        Point3D(0.0, 1.0, 0.0),
    ]
    faces = [(0, 1, 2), (0, 2, 3)]

    mesh = TriMesh(nodes=nodes, faces=faces)
    solver = ABFPlusPlus(mesh)

    assert 0 in solver.adj[1]
    assert 1 in solver.adj[0]


def test_abf_original_angles():
    from compgeom.mesh.surface.trimesh.trimesh import TriMesh
    from compgeom.mesh.surface.abf_plus_plus import ABFPlusPlus
    from compgeom.kernel import Point3D

    nodes = [
        Point3D(0.0, 0.0, 0.0),
        Point3D(1.0, 0.0, 0.0),
        Point3D(1.0, 1.0, 0.0),
        Point3D(0.0, 1.0, 0.0),
    ]
    faces = [(0, 1, 2), (0, 2, 3)]

    mesh = TriMesh(nodes=nodes, faces=faces)
    solver = ABFPlusPlus(mesh)

    angles = solver.compute_original_angles()
    assert angles.shape == (2, 3)


def test_abf_parameterization():
    from compgeom.mesh.surface.trimesh.trimesh import TriMesh
    from compgeom.mesh.surface.abf_plus_plus import ABFPlusPlus
    from compgeom.kernel import Point3D

    nodes = [
        Point3D(0.0, 0.0, 0.0),
        Point3D(1.0, 0.0, 0.0),
        Point3D(1.0, 1.0, 0.0),
        Point3D(0.0, 1.0, 0.0),
    ]
    faces = [(0, 1, 2), (0, 2, 3)]

    mesh = TriMesh(nodes=nodes, faces=faces)
    solver = ABFPlusPlus(mesh)

    u, v = solver.compute_parameterization(iterations=10)
    assert len(u) == 4
    assert len(v) == 4


def test_abf_wrapper():
    from compgeom.mesh.surface.trimesh.trimesh import TriMesh
    from compgeom.mesh.surface.abf_plus_plus import ABFParameterization
    from compgeom.kernel import Point3D

    nodes = [
        Point3D(0.0, 0.0, 0.0),
        Point3D(1.0, 0.0, 0.0),
        Point3D(1.0, 1.0, 0.0),
        Point3D(0.0, 1.0, 0.0),
    ]
    faces = [(0, 1, 2), (0, 2, 3)]

    mesh = TriMesh(nodes=nodes, faces=faces)
    wrapper = ABFParameterization(mesh)

    uv = wrapper.compute(iterations=5)
    assert len(uv) == 4
    assert all(isinstance(c, tuple) and len(c) == 2 for c in uv)


def test_abf_convenience():
    from compgeom.mesh.surface.trimesh.trimesh import TriMesh
    from compgeom.mesh.surface.abf_plus_plus import abf_plus_plus
    from compgeom.kernel import Point3D

    nodes = [
        Point3D(0.0, 0.0, 0.0),
        Point3D(1.0, 0.0, 0.0),
        Point3D(1.0, 1.0, 0.0),
        Point3D(0.0, 1.0, 0.0),
    ]
    faces = [(0, 1, 2), (0, 2, 3)]

    mesh = TriMesh(nodes=nodes, faces=faces)
    uv = abf_plus_plus(mesh, iterations=5)

    assert len(uv) == 4
    assert all(isinstance(c, tuple) and len(c) == 2 for c in uv)
