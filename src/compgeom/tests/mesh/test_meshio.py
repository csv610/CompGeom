import os
import pytest
from compgeom.kernel import Point2D, Point3D
from compgeom.mesh.mesh import TriMesh
from compgeom.mesh.meshio import (
    OBJFileHandler,
    OFFFileHandler,
    STLFileHandler,
    PLYFileHandler,
    MeshImporter,
    MeshExporter,
)

@pytest.fixture
def sample_mesh():
    vertices = [Point3D(0, 0, 0, 0), Point3D(1, 0, 0, 1), Point3D(0, 1, 0, 2)]
    faces = [(0, 1, 2)]
    return TriMesh(vertices, faces)

def test_obj_io(sample_mesh, tmp_path):
    filename = str(tmp_path / 'test.obj')
    OBJFileHandler.write(filename, sample_mesh)
    
    mesh = OBJFileHandler.read(filename)
    assert len(mesh.vertices) == 3
    assert len(mesh.elements) == 1
    assert mesh.vertices[1].x == 1.0

def test_off_io(sample_mesh, tmp_path):
    filename = str(tmp_path / 'test.off')
    OFFFileHandler.write(filename, sample_mesh)
    
    mesh = OFFFileHandler.read(filename)
    assert len(mesh.vertices) == 3
    assert len(mesh.elements) == 1

def test_stl_ascii_io(sample_mesh, tmp_path):
    filename = str(tmp_path / 'test_ascii.stl')
    STLFileHandler.write(filename, sample_mesh, binary=False)
    
    mesh = STLFileHandler.read(filename)
    assert len(mesh.vertices) == 3
    assert len(mesh.elements) == 1

def test_stl_binary_io(sample_mesh, tmp_path):
    filename = str(tmp_path / 'test_bin.stl')
    STLFileHandler.write(filename, sample_mesh, binary=True)
    
    mesh = STLFileHandler.read(filename)
    assert len(mesh.vertices) == 3
    assert len(mesh.elements) == 1

def test_ply_ascii_io(sample_mesh, tmp_path):
    filename = str(tmp_path / 'test_ascii.ply')
    PLYFileHandler.write(filename, sample_mesh, binary=False)
    
    mesh = PLYFileHandler.read(filename)
    assert len(mesh.vertices) == 3
    assert len(mesh.elements) == 1

def test_ply_binary_io(sample_mesh, tmp_path):
    filename = str(tmp_path / 'test_bin.ply')
    PLYFileHandler.write(filename, sample_mesh, binary=True)
    
    mesh = PLYFileHandler.read(filename)
    assert len(mesh.vertices) == 3
    assert len(mesh.elements) == 1

def test_unified_importer_exporter(sample_mesh, tmp_path):
    filename = str(tmp_path / 'test_unified.obj')
    MeshExporter.write(filename, sample_mesh)
    
    mesh = MeshImporter.read(filename)
    assert len(mesh.vertices) == 3
    assert len(mesh.elements) == 1
