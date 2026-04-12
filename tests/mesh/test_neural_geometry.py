"""Unit tests for Neural and Implicit Geometry algorithms."""

import pytest
import numpy as np
from compgeom.mesh.surface.neural_reconstruction import NeuralDualContourer
from compgeom.mesh.surface.neural_winding import NeuralWindingLifter
from compgeom.mesh.surface.lipschitz_sdf import LipschitzSDF

def test_neural_dual_contouring():
    # Mock SDF function for a sphere radius 0.5
    def sphere_sdf(p):
        return np.linalg.norm(p, axis=1, keepdims=True) - 0.5
    
    ndc = NeuralDualContourer(sphere_sdf)
    mesh = ndc.reconstruct(np.array([-1, -1, -1]), np.array([1, 1, 1]), grid_res=8)
    # We expect some dual vertices to be generated
    assert len(mesh.vertices) > 0

def test_neural_winding_lifter():
    # Mock neural SDF
    def mock_sdf(p):
        return np.ones((len(p), 1))
    
    lifter = NeuralWindingLifter(mock_sdf)
    res = lifter.evaluate_lifted(np.array([[0.5, 0.5, 0.5]]))
    assert res.shape == (1, 1)

def test_lipschitz_sdf():
    import torch
    sdf = LipschitzSDF()
    inp = torch.randn(1, 3)
    out = sdf(inp)
    assert out.shape == (1, 1)
