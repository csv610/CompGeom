"""Tests for Discrete Circle Packing."""

import numpy as np
import pytest


def test_circle_packing_import():
    from compgeom.mesh.surface.circle_packing import (
        CirclePacking,
        ThurstonCirclePacking,
        discrete_circle_packing,
    )

    assert CirclePacking is not None
    assert ThurstonCirclePacking is not None
    assert discrete_circle_packing is not None


def test_mesh_init_import_from_main():
    from compgeom.mesh import (
        CirclePacking,
        ThurstonCirclePacking,
        discrete_circle_packing,
    )

    assert CirclePacking is not None
    assert ThurstonCirclePacking is not None
    assert discrete_circle_packing is not None


def test_circle_packing_init():
    from compgeom.mesh.surface.trimesh.trimesh import TriMesh
    from compgeom.mesh.surface.circle_packing import CirclePacking
    from compgeom.kernel import Point3D

    nodes = [
        Point3D(0.0, 0.0, 0.0),
        Point3D(1.0, 0.0, 0.0),
        Point3D(1.0, 1.0, 0.0),
        Point3D(0.0, 1.0, 0.0),
    ]
    faces = [(0, 1, 2), (0, 2, 3)]

    mesh = TriMesh(nodes=nodes, faces=faces)
    packing = CirclePacking(mesh)

    assert packing.num_v == 4
    assert packing.num_f == 2
    assert len(packing.radii) == 4


def test_circle_packing_adjacency():
    from compgeom.mesh.surface.trimesh.trimesh import TriMesh
    from compgeom.mesh.surface.circle_packing import CirclePacking
    from compgeom.kernel import Point3D

    nodes = [
        Point3D(0.0, 0.0, 0.0),
        Point3D(1.0, 0.0, 0.0),
        Point3D(1.0, 1.0, 0.0),
        Point3D(0.0, 1.0, 0.0),
    ]
    faces = [(0, 1, 2), (0, 2, 3)]

    mesh = TriMesh(nodes=nodes, faces=faces)
    packing = CirclePacking(mesh)

    assert 0 in packing.adj[1]
    assert 1 in packing.adj[0]
    assert len(packing.edges) > 0


def test_ricci_flow():
    from compgeom.mesh.surface.trimesh.trimesh import TriMesh
    from compgeom.mesh.surface.circle_packing import CirclePacking
    from compgeom.kernel import Point3D

    nodes = [
        Point3D(0.0, 0.0, 0.0),
        Point3D(1.0, 0.0, 0.0),
        Point3D(1.0, 1.0, 0.0),
        Point3D(0.0, 1.0, 0.0),
    ]
    faces = [(0, 1, 2), (0, 2, 3)]

    mesh = TriMesh(nodes=nodes, faces=faces)
    packing = CirclePacking(mesh)

    radii = packing.ricci_flow(iterations=10)
    assert len(radii) == 4
    assert all(r > 0 for r in radii)


def test_thurston_packing():
    from compgeom.mesh.surface.trimesh.trimesh import TriMesh
    from compgeom.mesh.surface.circle_packing import ThurstonCirclePacking
    from compgeom.kernel import Point3D

    nodes = [
        Point3D(0.0, 0.0, 0.0),
        Point3D(1.0, 0.0, 0.0),
        Point3D(1.0, 1.0, 0.0),
        Point3D(0.0, 1.0, 0.0),
    ]
    faces = [(0, 1, 2), (0, 2, 3)]

    mesh = TriMesh(nodes=nodes, faces=faces)
    packing = ThurstonCirclePacking(mesh)

    radii = packing.solve(max_iterations=10)
    assert len(radii) == 4
    assert all(r > 0 for r in radii)


def test_conformal_factor():
    from compgeom.mesh.surface.trimesh.trimesh import TriMesh
    from compgeom.mesh.surface.circle_packing import CirclePacking
    from compgeom.kernel import Point3D

    nodes = [
        Point3D(0.0, 0.0, 0.0),
        Point3D(1.0, 0.0, 0.0),
        Point3D(1.0, 1.0, 0.0),
        Point3D(0.0, 1.0, 0.0),
    ]
    faces = [(0, 1, 2), (0, 2, 3)]

    mesh = TriMesh(nodes=nodes, faces=faces)
    packing = CirclePacking(mesh)
    packing.ricci_flow(iterations=5)

    factor = packing.conformal_factor_at_vertices()
    assert len(factor) == 4
