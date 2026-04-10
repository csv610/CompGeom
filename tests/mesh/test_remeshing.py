"""Unit tests for Remeshing algorithms (Non-Obtuse Triangulation, TriWild)."""

import pytest
from compgeom.kernel import Point2D, Point3D
from compgeom.mesh.surface.trimesh.trimesh import TriMesh
from compgeom.mesh.surface.trimesh.non_obtuse_triangulation import NonObtuseTriangulator
from compgeom.mesh.surface.angle_bounded_remesher import AngleBoundedRemesher

@pytest.fixture
def simple_mesh():
    verts = [Point3D(0, 0, 0), Point3D(1, 0, 0), Point3D(0, 1, 0), Point3D(0, 0, 1)]
    faces = [(0, 1, 2), (0, 1, 3), (1, 2, 3), (2, 0, 3)]
    return TriMesh(verts, faces)

def test_non_obtuse_triangulator():
    # Obtuse triangle points
    pts = [Point2D(0, 0), Point2D(10, 0), Point2D(5, 0.1)]
    notri = NonObtuseTriangulator(pts)
    mesh = notri.triangulate(max_steiner=10)
    assert len(mesh.vertices) >= 3

def test_angle_bounded_remesher(simple_mesh):
    remesher = AngleBoundedRemesher(simple_mesh)
    out = remesher.remesh(iterations=1)
    assert len(out.vertices) == len(simple_mesh.vertices)
