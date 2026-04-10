"""Unit tests for Surface Reconstruction algorithms."""

import pytest
import numpy as np
from compgeom.mesh.surface.poisson_manifold import PoissonManifold

def test_poisson_manifold():
    pts = np.array([[0,0,0], [1,0,0], [2,0,0]])
    vecs = np.array([[1,0,0], [1,0,0], [1,0,0]])
    pm = PoissonManifold(pts, vecs)
    curve = pm.reconstruct_curve(np.array([-1,-1,-1]), np.array([3,1,1]), res=8)
    assert len(curve) > 0
