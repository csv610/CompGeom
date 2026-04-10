"""Unit tests for Mesh Geodesics algorithms."""

import pytest
from compgeom.kernel import Point3D
from compgeom.mesh.surface.trimesh.trimesh import TriMesh
from compgeom.mesh.algorithms.affine_heat import AffineHeatMethod

@pytest.fixture
def simple_mesh():
    verts = [Point3D(0,0,0), Point3D(1,0,0), Point3D(0,1,0), Point3D(0,0,1)]
    faces = [(0,1,2), (0,1,3), (1,2,3), (2,0,3)]
    return TriMesh(verts, faces)

def test_affine_heat_method(simple_mesh):
    ahm = AffineHeatMethod(simple_mesh)
    dist = ahm.compute_log_map(source_idx=0)
    assert len(dist) == 4
    assert dist[0] == pytest.approx(0.0)
