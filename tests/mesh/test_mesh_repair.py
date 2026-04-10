"""Unit tests for Mesh Repair algorithms."""

import pytest
from compgeom.kernel import Point3D
from compgeom.mesh.surface.trimesh.trimesh import TriMesh
from compgeom.mesh.surface.instant_repair import InstantRepair

@pytest.fixture
def simple_disk():
    # A single square patch triangulated (2 triangles)
    verts = [Point3D(0,0,0), Point3D(1,0,0), Point3D(1,1,0), Point3D(0,1,0)]
    faces = [(0, 1, 2), (0, 2, 3)]
    return TriMesh(verts, faces)

def test_instant_repair_init(simple_disk):
    repairer = InstantRepair(simple_disk)
    # No intersections in a simple disk
    repaired = repairer.repair()
    assert len(repaired.faces) == len(simple_disk.faces)
