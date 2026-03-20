"""Unit tests for DEC and Hodge Theory."""
import pytest
import numpy as np
from compgeom.kernel import Point3D
from compgeom.mesh.surface.trimesh.trimesh import TriMesh
from compgeom.mesh.surface.halfedge_mesh import HalfEdgeMesh
from compgeom.mesh.algorithms.dec import DEC
from compgeom.mesh.algorithms.hodge_theory import HodgeDecomposition

@pytest.fixture
def flat_mesh():
    # 2x2 grid (9 vertices, 8 faces)
    verts = []
    for i in range(3):
        for j in range(3):
            verts.append(Point3D(i, j, 0))
    faces = []
    for i in range(2):
        for j in range(2):
            v0 = i*3 + j
            v1 = (i+1)*3 + j
            v2 = (i+1)*3 + (j+1)
            v3 = i*3 + (j+1)
            faces.append((v0, v1, v2))
            faces.append((v0, v2, v3))
    return TriMesh(verts, faces)

def test_dec_stokes(flat_mesh):
    he_mesh = HalfEdgeMesh.from_triangle_mesh(flat_mesh)
    dec = DEC(he_mesh)
    
    d0 = dec.d0()
    d1 = dec.d1()
    
    # d1 * d0 should be zero
    res = d1 @ d0
    assert np.allclose(res.toarray(), 0.0)

def test_hodge_decomposition_exact(flat_mesh):
    he_mesh = HalfEdgeMesh.from_triangle_mesh(flat_mesh)
    hd = HodgeDecomposition(he_mesh)
    
    # Create an exact 1-form: omega = d * phi
    phi = np.random.rand(hd.dec.num_v)
    omega = hd.d0 @ phi
    
    exact, co_exact, harmonic = hd.decompose(omega)
    
    # Since omega is exact, it should be recovered fully
    assert np.allclose(exact, omega)
    assert np.allclose(co_exact, 0.0, atol=1e-7)
    assert np.allclose(harmonic, 0.0, atol=1e-7)

def test_hodge_orthogonality(flat_mesh):
    he_mesh = HalfEdgeMesh.from_triangle_mesh(flat_mesh)
    hd = HodgeDecomposition(he_mesh)
    
    # Random 1-form
    omega = np.random.rand(hd.dec.num_e)
    exact, co_exact, harmonic = hd.decompose(omega)
    
    # Orthogonality under L2 inner product: <a, b> = a.T * s1 * b
    s1 = hd.s1
    
    # exact . co_exact
    dot_ec = exact.T @ s1 @ co_exact
    assert abs(dot_ec) < 1e-7
    
    # exact . harmonic
    dot_eh = exact.T @ s1 @ harmonic
    assert abs(dot_eh) < 1e-7
    
    # co_exact . harmonic
    dot_ch = co_exact.T @ s1 @ harmonic
    assert abs(dot_ch) < 1e-4
