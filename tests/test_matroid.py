"""Tests for Matroid Theory."""

import numpy as np
import pytest


def test_matroid_import():
    from compgeom.mesh.algorithms.matroid import (
        Matroid,
        GraphicMatroid,
        MeshGraphicMatroid,
        create_graphic_matroid,
    )

    assert GraphicMatroid is not None
    assert MeshGraphicMatroid is not None


def test_mesh_init_import_from_main():
    from compgeom.mesh import (
        GraphicMatroid,
        create_graphic_matroid,
    )

    assert GraphicMatroid is not None
    assert create_graphic_matroid is not None


def test_graphic_matroid_init():
    from compgeom.mesh.algorithms.matroid import GraphicMatroid

    edges = [(0, 1), (1, 2), (2, 0)]
    matroid = GraphicMatroid(edges, 3)

    assert matroid.num_vertices == 3
    assert len(matroid.edges) == 3


def test_graphic_matroid_rank():
    from compgeom.mesh.algorithms.matroid import GraphicMatroid

    edges = [(0, 1), (1, 2), (2, 0)]
    matroid = GraphicMatroid(edges, 3)

    rank_empty = matroid.rank(set())
    assert rank_empty == 0

    rank_one = matroid.rank({0})
    assert rank_one >= 1

    rank_cycle = matroid.rank({0, 1, 2})
    assert rank_cycle == 2


def test_graphic_matroid_independent():
    from compgeom.mesh.algorithms.matroid import GraphicMatroid

    edges = [(0, 1), (1, 2), (2, 0)]
    matroid = GraphicMatroid(edges, 3)

    assert matroid.is_independent({0, 1}) == True
    assert matroid.is_independent({0, 1, 2}) == False


def test_graphic_matroid_circuit():
    from compgeom.mesh.algorithms.matroid import GraphicMatroid

    edges = [(0, 1), (1, 2), (2, 0)]
    matroid = GraphicMatroid(edges, 3)

    circuit = matroid.find_circuit({0, 1}, 2)
    assert isinstance(circuit, set)


def test_graphic_matroid_fundamental_circuits():
    from compgeom.mesh.algorithms.matroid import GraphicMatroid

    edges = [(0, 1), (1, 2), (2, 0)]
    matroid = GraphicMatroid(edges, 3)

    fund_circuits = matroid.fundamental_circuits({0, 1, 2})
    assert 2 in fund_circuits


def test_cut_edges():
    from compgeom.mesh.surface.trimesh.trimesh import TriMesh
    from compgeom.mesh.algorithms.matroid import MeshGraphicMatroid
    from compgeom.kernel import Point3D

    nodes = [
        Point3D(0.0, 0.0, 0.0),
        Point3D(1.0, 0.0, 0.0),
        Point3D(1.0, 1.0, 0.0),
        Point3D(0.0, 1.0, 0.0),
    ]
    faces = [(0, 1, 2), (0, 2, 3)]

    mesh = TriMesh(nodes=nodes, faces=faces)
    matroid = MeshGraphicMatroid(mesh)

    cut_edges = matroid.find_cut_edges()
    assert isinstance(cut_edges, set)


def test_cycle_edges():
    from compgeom.mesh.surface.trimesh.trimesh import TriMesh
    from compgeom.mesh.algorithms.matroid import MeshGraphicMatroid
    from compgeom.kernel import Point3D

    nodes = [
        Point3D(0.0, 0.0, 0.0),
        Point3D(1.0, 0.0, 0.0),
        Point3D(1.0, 1.0, 0.0),
        Point3D(0.0, 1.0, 0.0),
    ]
    faces = [(0, 1, 2), (0, 2, 3)]

    mesh = TriMesh(nodes=nodes, faces=faces)
    matroid = MeshGraphicMatroid(mesh)

    cycle_edges = matroid.find_cycle_edges()
    assert isinstance(cycle_edges, set)


def test_convenience():
    from compgeom.mesh.surface.trimesh.trimesh import TriMesh
    from compgeom.mesh.algorithms.matroid import create_graphic_matroid
    from compgeom.kernel import Point3D

    nodes = [
        Point3D(0.0, 0.0, 0.0),
        Point3D(1.0, 0.0, 0.0),
        Point3D(1.0, 1.0, 0.0),
    ]
    faces = [(0, 1, 2)]

    mesh = TriMesh(nodes=nodes, faces=faces)
    matroid = create_graphic_matroid(mesh)

    assert matroid is not None
    assert matroid.num_vertices == 3
