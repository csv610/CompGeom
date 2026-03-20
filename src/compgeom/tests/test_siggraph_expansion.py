"""
Unit tests for SIGGRAPH 2015-2025 algorithm expansion.
"""

import pytest
import numpy as np
from compgeom.kernel import Point2D, Point3D
from compgeom.mesh.surface.trimesh.trimesh import TriMesh
from compgeom.mesh.surface.parameterization_bff import BFFParameterizer
from compgeom.mesh.volume.tetmesh.robust_mesher import RobustTetMesher
from compgeom.mesh.algorithms.stochastic_pde import WalkOnSpheres
from compgeom.mesh.volume.neural_reconstruction import NeuralDualContourer
from compgeom.mesh.surface.instant_repair import InstantRepair
from compgeom.mesh.volume.neural_winding import NeuralWindingLifter

@pytest.fixture
def simple_disk():
    # A single square patch triangulated (2 triangles)
    verts = [Point3D(0,0,0), Point3D(1,0,0), Point3D(1,1,0), Point3D(0,1,0)]
    faces = [(0, 1, 2), (0, 2, 3)]
    return TriMesh(verts, faces)

def test_bff_initialization(simple_disk):
    bff = BFFParameterizer(simple_disk)
    assert bff.num_v == 4
    assert bff.L is not None

def test_robust_mesher_init():
    v = np.array([[0,0,0], [1,0,0], [0,1,0], [0,0,1]])
    f = np.array([[0,1,2], [0,2,3], [0,3,1], [1,2,3]])
    mesher = RobustTetMesher(v, f)
    assert len(mesher.vertices) == 4

def test_stochastic_pde_laplace(simple_disk):
    wos = WalkOnSpheres(simple_disk)
    # Solve Laplace for boundary values = constant 1.0
    # Expected result for any interior point should be 1.0
    val = wos.solve_laplace(Point3D(0.5, 0.5, 0), lambda p: 1.0, num_walks=10)
    assert 0.9 < val < 1.1

def test_neural_dual_contouring():
    # Mock SDF function for a sphere radius 0.5
    def sphere_sdf(p):
        return np.linalg.norm(p, axis=1, keepdims=True) - 0.5
    
    ndc = NeuralDualContourer(sphere_sdf)
    mesh = ndc.reconstruct(np.array([-1,-1,-1]), np.array([1,1,1]), grid_res=8)
    # We expect some dual vertices to be generated
    assert len(mesh.vertices) > 0

def test_instant_repair_init(simple_disk):
    repairer = InstantRepair(simple_disk)
    # No intersections in a simple disk
    repaired = repairer.repair()
    assert len(repaired.faces) == len(simple_disk.faces)

def test_neural_winding_lifter():
    # Mock neural SDF
    def mock_sdf(p):
        return np.ones((len(p), 1))
    
    lifter = NeuralWindingLifter(mock_sdf)
    res = lifter.evaluate_lifted(np.array([[0.5, 0.5, 0.5]]))
    assert res.shape == (1, 1)
