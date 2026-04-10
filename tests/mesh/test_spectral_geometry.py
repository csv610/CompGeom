"""Unit tests for Spectral Geometry algorithms (WKS, Functional Maps, SpectralNet)."""

import pytest
import numpy as np
from compgeom.kernel import Point3D
from compgeom.mesh.surface.trimesh.trimesh import TriMesh
from compgeom.mesh.algorithms.wave_kernel import WaveKernelSignature
from compgeom.mesh.algorithms.functional_maps import FunctionalMap
from compgeom.mesh.algorithms.shape_space_spectra import ShapeSpaceSpectralNet
from compgeom.mesh.volume.spectral_geometry import SpectralGeometry

@pytest.fixture
def simple_mesh():
    verts = [Point3D(0, 0, 0), Point3D(1, 0, 0), Point3D(0, 1, 0), Point3D(0, 0, 1)]
    faces = [(0, 1, 2), (0, 1, 3), (1, 2, 3), (2, 0, 3)]
    return TriMesh(verts, faces)

def test_wave_kernel_signature(simple_mesh):
    wks = WaveKernelSignature(simple_mesh, k=4)
    sig = wks.compute(num_scales=10)
    assert sig.shape == (4, 10)

def test_functional_maps(simple_mesh):
    # Match a mesh with itself
    k = 4
    fm = FunctionalMap(simple_mesh, simple_mesh, k=k)
    C = fm.compute_map()
    expected_k = min(k, len(simple_mesh.vertices) - 1)
    assert C.shape == (expected_k, expected_k)
    # Identity correspondence
    corr = fm.vertex_correspondence(C)
    assert len(corr) == 4

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

def test_diffusion_distance(simple_mesh):
    # Diffusion distance should be 0 between same vertex
    dist_same = SpectralGeometry.compute_diffusion_distance(simple_mesh, 0, 0, t=1.0, k=3)
    assert dist_same == pytest.approx(0.0)
    
    # Diffusion distance between different vertices should be positive
    dist_diff = SpectralGeometry.compute_diffusion_distance(simple_mesh, 0, 1, t=1.0, k=3)
    assert dist_diff > 0.0
    
    # Check embedding shape
    emb = SpectralGeometry.compute_diffusion_embedding(simple_mesh, t=1.0, k=3)
    assert emb.shape == (4, 3)
