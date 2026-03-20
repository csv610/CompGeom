"""Unit tests for SIGGRAPH 2025/2026 expansion."""
import pytest
import numpy as np
from compgeom.kernel import Point3D
from compgeom.mesh.surface.trimesh.trimesh import TriMesh
from compgeom.mesh.algorithms.stochastic_pde import WalkOnStars
from compgeom.mesh.algorithms.shape_space_spectra import ShapeSpaceSpectralNet
from compgeom.mesh.volume.odeco_frame_field import OdecoFrameField
from compgeom.mesh.volume.tetmesh.tetmesh import TetMesh

@pytest.fixture
def simple_trimesh():
    verts = [Point3D(0,0,0), Point3D(1,0,0), Point3D(0,1,0), Point3D(0,0,1)]
    faces = [(0,1,2), (0,1,3), (1,2,3), (2,0,3)]
    return TriMesh(verts, faces)

@pytest.fixture
def simple_tetmesh():
    nodes = [Point3D(0,0,0), Point3D(1,0,0), Point3D(0,1,0), Point3D(0,0,1)]
    cells = [(0,1,2,3)]
    return TetMesh(nodes, cells)

def test_walk_on_stars_gradient(simple_trimesh):
    wost = WalkOnStars(simple_trimesh)
    # Estimate gradient of a linear field u(x,y,z) = x
    # grad u should be (1, 0, 0)
    # We use a point far from the boundary to ensure stability
    grad = wost.solve_gradient(Point3D(0.1, 0.1, 0.1), lambda p: p.x, num_walks=200)
    assert len(grad) == 3
    # Check if x-component is significantly larger than noise
    assert abs(grad[0]) > abs(grad[1])
    assert abs(grad[0]) > abs(grad[2])

def test_shape_space_spectra_init():
    try:
        import torch
        net = ShapeSpaceSpectralNet(num_eigen=5)
        x = torch.randn(10, 3)
        theta = torch.randn(10, 8)
        phi = net(x, theta)
        assert phi.shape == (10, 5)
    except ImportError:
        pytest.skip("Torch not found")

def test_odeco_frame_field(simple_tetmesh):
    off = OdecoFrameField(simple_tetmesh)
    assert len(off.frames) == 1
    
    # Align to a normal (1, 0, 0)
    off.align_to_boundary(np.array([[1.0, 0.0, 0.0]]), np.array([0]))
    frame = off.frames[0]
    # One axis should be (1, 0, 0)
    assert np.allclose(frame.axes[:, 0], [1, 0, 0])
    # Stretching should be isotropic by default
    assert off.get_anisotropy(0) == pytest.approx(1.0)
