"""Tests for Conformal Shape Registration."""

import numpy as np
import pytest


def test_registration_import():
    from compgeom.mesh.surface.conformal_registration import (
        ConformalShapeRegistration,
        FunctionalMap,
        ConformalMorph,
        register_conformal_shapes,
        conformal_morph,
    )

    assert ConformalShapeRegistration is not None
    assert FunctionalMap is not None


def test_mesh_init_import_from_main():
    from compgeom.mesh import (
        ConformalShapeRegistration,
        register_conformal_shapes,
    )

    assert ConformalShapeRegistration is not None
    assert register_conformal_shapes is not None


def test_registration_init():
    from compgeom.mesh.surface.trimesh.trimesh import TriMesh
    from compgeom.mesh.surface.conformal_registration import ConformalShapeRegistration
    from compgeom.kernel import Point3D

    source_nodes = [
        Point3D(0.0, 0.0, 0.0),
        Point3D(1.0, 0.0, 0.0),
        Point3D(1.0, 1.0, 0.0),
    ]
    source_faces = [(0, 1, 2)]

    target_nodes = [
        Point3D(0.0, 0.0, 0.0),
        Point3D(0.5, 0.0, 0.0),
        Point3D(0.5, 0.5, 0.0),
    ]
    target_faces = [(0, 1, 2)]

    source = TriMesh(nodes=source_nodes, faces=source_faces)
    target = TriMesh(nodes=target_nodes, faces=target_faces)

    reg = ConformalShapeRegistration(source, target)

    assert reg.source_num_v == 3
    assert reg.target_num_v == 3


def test_registration_adjacency():
    from compgeom.mesh.surface.trimesh.trimesh import TriMesh
    from compgeom.mesh.surface.conformal_registration import ConformalShapeRegistration
    from compgeom.kernel import Point3D

    source_nodes = [
        Point3D(0.0, 0.0, 0.0),
        Point3D(1.0, 0.0, 0.0),
        Point3D(1.0, 1.0, 0.0),
    ]
    source_faces = [(0, 1, 2)]

    target_nodes = [
        Point3D(0.0, 0.0, 0.0),
        Point3D(0.5, 0.0, 0.0),
        Point3D(0.5, 0.5, 0.0),
    ]
    target_faces = [(0, 1, 2)]

    source = TriMesh(nodes=source_nodes, faces=source_faces)
    target = TriMesh(nodes=target_nodes, faces=target_faces)

    reg = ConformalShapeRegistration(source, target)

    assert len(reg.source_adj[0]) >= 1


def test_registration_register():
    from compgeom.mesh.surface.trimesh.trimesh import TriMesh
    from compgeom.mesh.surface.conformal_registration import ConformalShapeRegistration
    from compgeom.kernel import Point3D

    source_nodes = [
        Point3D(0.0, 0.0, 0.0),
        Point3D(1.0, 0.0, 0.0),
        Point3D(1.0, 1.0, 0.0),
    ]
    source_faces = [(0, 1, 2)]

    target_nodes = [
        Point3D(0.0, 0.0, 0.0),
        Point3D(0.5, 0.0, 0.0),
        Point3D(0.5, 0.5, 0.0),
    ]
    target_faces = [(0, 1, 2)]

    source = TriMesh(nodes=source_nodes, faces=source_faces)
    target = TriMesh(nodes=target_nodes, faces=target_faces)

    reg = ConformalShapeRegistration(source, target)
    transformed, T = reg.register(iterations=5)

    assert transformed.shape[0] == 3
    assert T.shape == (3, 3)


def test_functional_map():
    from compgeom.mesh.surface.trimesh.trimesh import TriMesh
    from compgeom.mesh.surface.conformal_registration import FunctionalMap
    from compgeom.kernel import Point3D

    source_nodes = [
        Point3D(0.0, 0.0, 0.0),
        Point3D(1.0, 0.0, 0.0),
        Point3D(1.0, 1.0, 0.0),
    ]
    source_faces = [(0, 1, 2)]

    target_nodes = [
        Point3D(0.0, 0.0, 0.0),
        Point3D(0.5, 0.0, 0.0),
        Point3D(0.5, 0.5, 0.0),
    ]
    target_faces = [(0, 1, 2)]

    source = TriMesh(nodes=source_nodes, faces=source_faces)
    target = TriMesh(nodes=target_nodes, faces=target_faces)

    fmap = FunctionalMap(source, target)
    C = fmap.compute_functional_map(k=3)

    assert C is not None


def test_conformal_morph():
    from compgeom.mesh.surface.trimesh.trimesh import TriMesh
    from compgeom.mesh.surface.conformal_registration import ConformalMorph
    from compgeom.kernel import Point3D

    source_nodes = [
        Point3D(0.0, 0.0, 0.0),
        Point3D(1.0, 0.0, 0.0),
        Point3D(1.0, 1.0, 0.0),
    ]
    source_faces = [(0, 1, 2)]

    target_nodes = [
        Point3D(0.0, 0.0, 0.0),
        Point3D(0.5, 0.0, 0.0),
        Point3D(0.5, 0.5, 0.0),
    ]
    target_faces = [(0, 1, 2)]

    source = TriMesh(nodes=source_nodes, faces=source_faces)
    target = TriMesh(nodes=target_nodes, faces=target_faces)

    morph = ConformalMorph(source, target)
    sequence = morph.morph(steps=3)

    assert len(sequence) == 3
    assert sequence[0].shape[0] == 3


def test_convenience():
    from compgeom.mesh.surface.trimesh.trimesh import TriMesh
    from compgeom.mesh.surface.conformal_registration import register_conformal_shapes
    from compgeom.kernel import Point3D

    source_nodes = [
        Point3D(0.0, 0.0, 0.0),
        Point3D(1.0, 0.0, 0.0),
        Point3D(1.0, 1.0, 0.0),
    ]
    source_faces = [(0, 1, 2)]

    target_nodes = [
        Point3D(0.0, 0.0, 0.0),
        Point3D(0.5, 0.0, 0.0),
        Point3D(0.5, 0.5, 0.0),
    ]
    target_faces = [(0, 1, 2)]

    source = TriMesh(nodes=source_nodes, faces=source_faces)
    target = TriMesh(nodes=target_nodes, faces=target_faces)

    transformed, T = register_conformal_shapes(source, target)

    assert transformed.shape[0] == 3
