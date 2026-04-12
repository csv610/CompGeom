"""Tests for Discrete Yamabe Flow."""

import numpy as np
import pytest


def test_yamabe_import():
    from compgeom.mesh.surface.yamabe_flow import (
        DiscreteYamabeFlow,
        YamabeFlowParameterization,
        yamabe_flow,
    )

    assert DiscreteYamabeFlow is not None
    assert YamabeFlowParameterization is not None


def test_mesh_init_import_from_main():
    from compgeom.mesh import (
        DiscreteYamabeFlow,
        yamabe_flow,
    )

    assert DiscreteYamabeFlow is not None
    assert yamabe_flow is not None


def test_yamabe_init():
    from compgeom.mesh.surface.trimesh.trimesh import TriMesh
    from compgeom.mesh.surface.yamabe_flow import DiscreteYamabeFlow
    from compgeom.kernel import Point3D

    nodes = [
        Point3D(0.0, 0.0, 0.0),
        Point3D(1.0, 0.0, 0.0),
        Point3D(1.0, 1.0, 0.0),
        Point3D(0.0, 1.0, 0.0),
    ]
    faces = [(0, 1, 2), (0, 2, 3)]

    mesh = TriMesh(nodes=nodes, faces=faces)
    solver = DiscreteYamabeFlow(mesh)

    assert solver.num_v == 4
    assert solver.num_f == 2


def test_yamabe_adjacency():
    from compgeom.mesh.surface.trimesh.trimesh import TriMesh
    from compgeom.mesh.surface.yamabe_flow import DiscreteYamabeFlow
    from compgeom.kernel import Point3D

    nodes = [
        Point3D(0.0, 0.0, 0.0),
        Point3D(1.0, 0.0, 0.0),
        Point3D(1.0, 1.0, 0.0),
        Point3D(0.0, 1.0, 0.0),
    ]
    faces = [(0, 1, 2), (0, 2, 3)]

    mesh = TriMesh(nodes=nodes, faces=faces)
    solver = DiscreteYamabeFlow(mesh)

    assert 0 in solver.adj[1]
    assert 1 in solver.adj[0]


def test_yamabe_area():
    from compgeom.mesh.surface.trimesh.trimesh import TriMesh
    from compgeom.mesh.surface.yamabe_flow import DiscreteYamabeFlow
    from compgeom.kernel import Point3D

    nodes = [
        Point3D(0.0, 0.0, 0.0),
        Point3D(1.0, 0.0, 0.0),
        Point3D(1.0, 1.0, 0.0),
        Point3D(0.0, 1.0, 0.0),
    ]
    faces = [(0, 1, 2), (0, 2, 3)]

    mesh = TriMesh(nodes=nodes, faces=faces)
    solver = DiscreteYamabeFlow(mesh)

    area = solver.compute_original_area()
    assert area > 0


def test_yamabe_evolve():
    from compgeom.mesh.surface.trimesh.trimesh import TriMesh
    from compgeom.mesh.surface.yamabe_flow import DiscreteYamabeFlow
    from compgeom.kernel import Point3D

    nodes = [
        Point3D(0.0, 0.0, 0.0),
        Point3D(1.0, 0.0, 0.0),
        Point3D(1.0, 1.0, 0.0),
        Point3D(0.0, 1.0, 0.0),
    ]
    faces = [(0, 1, 2), (0, 2, 3)]

    mesh = TriMesh(nodes=nodes, faces=faces)
    solver = DiscreteYamabeFlow(mesh)

    factors = solver.evolve(iterations=10)
    assert len(factors) == 4


def test_yamabe_conformal_map():
    from compgeom.mesh.surface.trimesh.trimesh import TriMesh
    from compgeom.mesh.surface.yamabe_flow import DiscreteYamabeFlow
    from compgeom.kernel import Point3D

    nodes = [
        Point3D(0.0, 0.0, 0.0),
        Point3D(1.0, 0.0, 0.0),
        Point3D(1.0, 1.0, 0.0),
        Point3D(0.0, 1.0, 0.0),
    ]
    faces = [(0, 1, 2), (0, 2, 3)]

    mesh = TriMesh(nodes=nodes, faces=faces)
    solver = DiscreteYamabeFlow(mesh)

    u, v = solver.compute_conformal_map(iterations=10)
    assert len(u) == 4
    assert len(v) == 4


def test_yamabe_wrapper():
    from compgeom.mesh.surface.trimesh.trimesh import TriMesh
    from compgeom.mesh.surface.yamabe_flow import YamabeFlowParameterization
    from compgeom.kernel import Point3D

    nodes = [
        Point3D(0.0, 0.0, 0.0),
        Point3D(1.0, 0.0, 0.0),
        Point3D(1.0, 1.0, 0.0),
        Point3D(0.0, 1.0, 0.0),
    ]
    faces = [(0, 1, 2), (0, 2, 3)]

    mesh = TriMesh(nodes=nodes, faces=faces)
    wrapper = YamabeFlowParameterization(mesh)

    uv = wrapper.compute(iterations=5)
    assert len(uv) == 4
    assert all(isinstance(c, tuple) and len(c) == 2 for c in uv)


def test_yamabe_convenience():
    from compgeom.mesh.surface.trimesh.trimesh import TriMesh
    from compgeom.mesh.surface.yamabe_flow import yamabe_flow
    from compgeom.kernel import Point3D

    nodes = [
        Point3D(0.0, 0.0, 0.0),
        Point3D(1.0, 0.0, 0.0),
        Point3D(1.0, 1.0, 0.0),
        Point3D(0.0, 1.0, 0.0),
    ]
    faces = [(0, 1, 2), (0, 2, 3)]

    mesh = TriMesh(nodes=nodes, faces=faces)
    uv = yamabe_flow(mesh, iterations=5)

    assert len(uv) == 4
    assert all(isinstance(c, tuple) and len(c) == 2 for c in uv)
