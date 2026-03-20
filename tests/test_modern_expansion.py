"""Comprehensive tests for Modern Computational Geometry Expansion (2015-2026)."""
import pytest
import numpy as np
from compgeom.kernel import Point3D, Point2D, AABB3D
from compgeom.mesh.surface.trimesh.trimesh import TriMesh
from compgeom.mesh.algorithms.affine_heat import AffineHeatMethod
from compgeom.mesh.algorithms.wave_kernel import WaveKernelSignature
from compgeom.mesh.algorithms.functional_maps import FunctionalMap
from compgeom.mesh.surface.non_obtuse_triangulation import NonObtuseTriangulator
from compgeom.mesh.surface.triwild import TriWildRemesher
from compgeom.mesh.surface.poisson_manifold import PoissonManifold
from compgeom.mesh.volume.lipschitz_sdf import LipschitzSDF
from compgeom.algo.contiguous_art_gallery import ContiguousArtGallery
from compgeom.algo.union_volume_estimation import UnionVolumeEstimator
from compgeom.spatial.kinetic_voronoi import KineticVoronoi, KineticPoint
from compgeom.polygon.polygon import Polygon

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

def test_wave_kernel_signature(simple_mesh):
    wks = WaveKernelSignature(simple_mesh, k=4)
    sig = wks.compute(num_scales=10)
    assert sig.shape == (4, 10)

def test_functional_maps(simple_mesh):
    # Match a mesh with itself
    k = 4
    fm = FunctionalMap(simple_mesh, simple_mesh, k=k)
    C = fm.compute_map()
    expected_k = min(k, 4 - 1)
    assert C.shape == (expected_k, expected_k)
    # Identity correspondence
    corr = fm.vertex_correspondence(C)
    assert len(corr) == 4

def test_non_obtuse_triangulator():
    # Obtuse triangle: (0,0), (10,0), (0.5, 0.1) - wait, (0,0),(10,0),(5, 0.1) is obtuse
    pts = [Point2D(0,0), Point2D(10,0), Point2D(5, 0.1)]
    notri = NonObtuseTriangulator(pts)
    mesh = notri.triangulate(max_steiner=10)
    assert len(mesh.vertices) >= 3

def test_triwild_remesher(simple_mesh):
    remesher = TriWildRemesher(simple_mesh)
    out = remesher.remesh(iterations=1)
    assert len(out.vertices) == len(simple_mesh.vertices)

def test_poisson_manifold():
    pts = np.array([[0,0,0], [1,0,0], [2,0,0]])
    vecs = np.array([[1,0,0], [1,0,0], [1,0,0]])
    pm = PoissonManifold(pts, vecs)
    curve = pm.reconstruct_curve(np.array([-1,-1,-1]), np.array([3,1,1]), res=8)
    assert len(curve) > 0

def test_lipschitz_sdf():
    try:
        sdf = LipschitzSDF()
        import torch
        inp = torch.randn(1, 3)
        out = sdf(inp)
        assert out.shape == (1, 1)
    except ImportError:
        pytest.skip("Torch not found")

def test_contiguous_art_gallery():
    poly = Polygon([Point2D(0,0), Point2D(2,0), Point2D(2,2), Point2D(0,2)])
    cag = ContiguousArtGallery(poly)
    guards = cag.solve()
    assert len(guards) > 0

def test_union_volume_estimation():
    bbox = AABB3D(-1, -1, -1, 1, 1, 1) # Smaller bbox
    uve = UnionVolumeEstimator(bbox, num_samples=1000)
    class MockObj:
        def contains(self, p): return np.linalg.norm(p) < 0.5
    vol = uve.estimate([MockObj()])
    # Sphere radius 0.5, vol ~ 0.52. BBox vol = 8.
    assert 0.1 < vol < 1.0

def test_kinetic_voronoi():
    pts = [KineticPoint(Point2D(0,0), (1,0)), KineticPoint(Point2D(10,10), (-1,0))]
    kv = KineticVoronoi(pts)
    kv.advance_to(1.0)
    assert kv.current_time == 1.0
