"""Unit tests for Advanced Conformal Geometry Expansion."""
import pytest
import numpy as np
import math
from compgeom.kernel import Point3D, Point2D
from compgeom.mesh.surface.trimesh.trimesh import TriMesh
from compgeom.mesh.surface.parameterization_lscm import LSCMParameterizer
from compgeom.mesh.surface.ricci_flow import RicciFlow
from compgeom.mesh.surface.conformal_equivalence import DiscreteConformalEquivalence
from compgeom.mesh.surface.quasi_conformal import QuasiConformalMap

@pytest.fixture
def flat_square():
    # 2 triangles forming a square
    verts = [Point3D(0,0,0), Point3D(1,0,0), Point3D(1,1,0), Point3D(0,1,0)]
    faces = [(0, 1, 2), (0, 2, 3)]
    return TriMesh(verts, faces)

def test_lscm_parameterization(flat_square):
    lscm = LSCMParameterizer(flat_square)
    uv = lscm.parameterize(pinned_indices=[0, 2], pinned_coords=[(0,0), (1,1)])
    assert len(uv) == 4
    # Fixed points should match exactly
    assert uv[0].x == pytest.approx(0.0)
    assert uv[2].x == pytest.approx(1.0)

def test_ricci_flow_initialization(flat_square):
    ricci = RicciFlow(flat_square)
    # Solve for flatness
    u = ricci.solve(max_iter=10)
    assert len(u) == 4
    lengths = ricci.get_edge_lengths()
    assert len(lengths) > 0

def test_discrete_conformal_equivalence_init(flat_square):
    dce = DiscreteConformalEquivalence(flat_square)
    assert dce.num_v == 4
    # Just a smoke test for parameterize call
    uv = dce.parameterize()
    assert len(uv) == 4

def test_quasi_conformal_landmarks(flat_square):
    qc = QuasiConformalMap(flat_square)
    # Map corners to themselves
    landmarks = [0, 1, 2, 3]
    coords = [(0,0), (1,0), (1,1), (0,1)]
    uv = qc.map_with_landmarks(landmarks, coords)
    assert len(uv) == 4
    for i in range(4):
        assert uv[i].x == pytest.approx(coords[i][0])
        assert uv[i].y == pytest.approx(coords[i][1])
