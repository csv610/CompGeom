"""Unit tests for Mesh Fields (Frame fields, Cross fields)."""

import pytest
import numpy as np
from compgeom.kernel import Point3D
from compgeom.mesh.volume.odeco_frame_field import OdecoFrameField
from compgeom.mesh.volume.tetmesh.tetmesh import TetMesh

@pytest.fixture
def simple_tetmesh():
    nodes = [Point3D(0, 0, 0), Point3D(1, 0, 0), Point3D(0, 1, 0), Point3D(0, 0, 1)]
    cells = [(0, 1, 2, 3)]
    return TetMesh(nodes, cells)

def test_odeco_frame_field_init(simple_tetmesh):
    off = OdecoFrameField(simple_tetmesh)
    assert len(off.frames) == 1
    # Isotropic identity by default
    M = off.frames[0].to_matrix()
    assert np.allclose(M, np.eye(3))

def test_odeco_frame_field_align(simple_tetmesh):
    off = OdecoFrameField(simple_tetmesh)
    # Align to a normal (1, 0, 0)
    off.align_to_boundary(np.array([[1.0, 0.0, 0.0]]), np.array([0]))
    frame = off.frames[0]
    # One axis should be (1, 0, 0)
    assert np.allclose(frame.axes[:, 0], [1, 0, 0])
    # Stretching should be isotropic by default
    assert off.get_anisotropy(0) == pytest.approx(1.0)
