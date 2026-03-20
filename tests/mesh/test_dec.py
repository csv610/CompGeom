
import pytest
import numpy as np
from scipy.sparse import csr_matrix
from compgeom.kernel import Point3D
from compgeom.mesh.surface.trimesh.trimesh import TriMesh
from compgeom.mesh.surface.halfedge_mesh import HalfEdgeMesh
from compgeom.mesh.algorithms.dec import DEC

@pytest.fixture
def simple_he_mesh():
    # Two triangles sharing edge (1,2)
    v = [Point3D(0,0,0), Point3D(1,0,0), Point3D(0,1,0), Point3D(1,1,0)]
    f = [(0,1,2), (1,3,2)]
    tm = TriMesh(v, f)
    return HalfEdgeMesh.from_triangle_mesh(tm)

def test_dec_init(simple_he_mesh):
    dec = DEC(simple_he_mesh)
    assert dec.num_v == 4
    assert dec.num_f == 2
    assert dec.num_e == 5

def test_dec_d0(simple_he_mesh):
    dec = DEC(simple_he_mesh)
    d0 = dec.d0()
    assert d0.shape == (5, 4)
    # d0 * constant_vector should be zero
    const = np.ones(4)
    res = d0.dot(const)
    assert np.allclose(res, 0)

def test_dec_d1(simple_he_mesh):
    dec = DEC(simple_he_mesh)
    d1 = dec.d1()
    assert d1.shape == (2, 5)
    # d1 * d0 should be zero
    d0 = dec.d0()
    res = d1.dot(d0.toarray())
    assert np.allclose(res, 0)

def test_dec_star0(simple_he_mesh):
    dec = DEC(simple_he_mesh)
    s0 = dec.star0()
    # Total area of two 0.5 area triangles is 1.0
    assert np.sum(s0.diagonal()) == pytest.approx(1.0)

def test_dec_star1(simple_he_mesh):
    dec = DEC(simple_he_mesh)
    s1 = dec.star1()
    assert s1.shape == (5, 5)
    # Check that diagonal is non-negative
    assert np.all(s1.diagonal() >= -1e-12)

def test_dec_star2(simple_he_mesh):
    dec = DEC(simple_he_mesh)
    s2 = dec.star2()
    # Two triangles of area 0.5 -> inverse areas are 2.0
    assert np.allclose(s2.diagonal(), 2.0)
