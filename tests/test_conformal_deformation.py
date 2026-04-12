"""Tests for Conformal Mesh Deformation."""

import numpy as np
import pytest


def test_conformal_deformation_import():
    from compgeom.mesh.surface.conformal_deformation import (
        ConformalDeformation,
        HarmonicConformalDeformation,
        conformal_deform,
        conformal_deform_rots,
    )

    assert ConformalDeformation is not None
    assert HarmonicConformalDeformation is not None


def test_mesh_init_import_from_main():
    from compgeom.mesh import (
        ConformalDeformation,
        conformal_deform,
    )

    assert ConformalDeformation is not None
    assert conformal_deform is not None


def test_conformal_deformation_init():
    from compgeom.mesh.surface.trimesh.trimesh import TriMesh
    from compgeom.mesh.surface.conformal_deformation import ConformalDeformation
    from compgeom.kernel import Point3D

    nodes = [
        Point3D(0.0, 0.0, 0.0),
        Point3D(1.0, 0.0, 0.0),
        Point3D(1.0, 1.0, 0.0),
        Point3D(0.0, 1.0, 0.0),
    ]
    faces = [(0, 1, 2), (0, 2, 3)]

    mesh = TriMesh(nodes=nodes, faces=faces)
    deform = ConformalDeformation(mesh)

    assert deform.num_v == 4
    assert deform.num_f == 2


def test_conformal_deformation_adjacency():
    from compgeom.mesh.surface.trimesh.trimesh import TriMesh
    from compgeom.mesh.surface.conformal_deformation import ConformalDeformation
    from compgeom.kernel import Point3D

    nodes = [
        Point3D(0.0, 0.0, 0.0),
        Point3D(1.0, 0.0, 0.0),
        Point3D(1.0, 1.0, 0.0),
        Point3D(0.0, 1.0, 0.0),
    ]
    faces = [(0, 1, 2), (0, 2, 3)]

    mesh = TriMesh(nodes=nodes, faces=faces)
    deform = ConformalDeformation(mesh)

    assert 0 in deform.adj[1]
    assert 1 in deform.adj[0]


def test_conformal_deformation_deform():
    from compgeom.mesh.surface.trimesh.trimesh import TriMesh
    from compgeom.mesh.surface.conformal_deformation import ConformalDeformation
    from compgeom.kernel import Point3D

    nodes = [
        Point3D(0.0, 0.0, 0.0),
        Point3D(1.0, 0.0, 0.0),
        Point3D(1.0, 1.0, 0.0),
        Point3D(0.0, 1.0, 0.0),
    ]
    faces = [(0, 1, 2), (0, 2, 3)]

    mesh = TriMesh(nodes=nodes, faces=faces)
    deform = ConformalDeformation(mesh)

    handle_vertices = [0]
    handle_positions = [np.array([0.0, 0.0, 0.0])]

    deformed = deform.deform(handle_vertices, handle_positions, iterations=3)

    assert deformed.shape == (4, 3)


def test_conformal_deformation_convenience():
    from compgeom.mesh.surface.trimesh.trimesh import TriMesh
    from compgeom.mesh.surface.conformal_deformation import conformal_deform
    from compgeom.kernel import Point3D

    nodes = [
        Point3D(0.0, 0.0, 0.0),
        Point3D(1.0, 0.0, 0.0),
        Point3D(1.0, 1.0, 0.0),
        Point3D(0.0, 1.0, 0.0),
    ]
    faces = [(0, 1, 2), (0, 2, 3)]

    mesh = TriMesh(nodes=nodes, faces=faces)
    deformed = conformal_deform(mesh, [0], [np.array([0.0, 0.0, 0.0])], iterations=3)

    assert deformed.shape == (4, 3)


def test_conformal_deformation_with_rots():
    from compgeom.mesh.surface.trimesh.trimesh import TriMesh
    from compgeom.mesh.surface.conformal_deformation import ConformalDeformation
    from compgeom.kernel import Point3D

    nodes = [
        Point3D(0.0, 0.0, 0.0),
        Point3D(1.0, 0.0, 0.0),
        Point3D(1.0, 1.0, 0.0),
        Point3D(0.0, 1.0, 0.0),
    ]
    faces = [(0, 1, 2), (0, 2, 3)]

    mesh = TriMesh(nodes=nodes, faces=faces)
    deform = ConformalDeformation(mesh)

    handle_vertices = [0]
    handle_positions = [np.array([0.0, 0.0, 0.0])]

    deformed = deform.deform_with_rots(handle_vertices, handle_positions, iterations=3)

    assert deformed.shape == (4, 3)


def test_harmonic_conformal_deformation():
    from compgeom.mesh.surface.trimesh.trimesh import TriMesh
    from compgeom.mesh.surface.conformal_deformation import HarmonicConformalDeformation
    from compgeom.kernel import Point3D

    nodes = [
        Point3D(0.0, 0.0, 0.0),
        Point3D(1.0, 0.0, 0.0),
        Point3D(1.0, 1.0, 0.0),
        Point3D(0.0, 1.0, 0.0),
    ]
    faces = [(0, 1, 2), (0, 2, 3)]

    mesh = TriMesh(nodes=nodes, faces=faces)
    deform = HarmonicConformalDeformation(mesh)

    handle_vertices = [0]
    handle_positions = [np.array([0.0, 0.0, 0.0])]

    deformed = deform.deform_harmonic(handle_vertices, handle_positions)

    assert deformed.shape == (4, 3)
