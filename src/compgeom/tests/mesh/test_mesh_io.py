import os
import pytest
from compgeom.kernel import Point2D, Point3D
from compgeom.mesh.mesh import TriangleMesh
from compgeom.mesh.mesh_io import OBJFileHandler, OFFFileHandler, STLFileHandler, PLYFileHandler, MeshImporter, MeshExporter

@pytest.fixture
def sample_mesh_data():
    vertices = [Point3D(0, 0, 0, 0), Point3D(1, 0, 0, 1), Point3D(0, 1, 0, 2)]
    faces = [(0, 1, 2)]
    return vertices, faces

def test_obj_io(sample_mesh_data, tmp_path):
    vertices, faces = sample_mesh_data
    filename = str(tmp_path / "test.obj")
    OBJFileHandler.write(filename, vertices, faces)
    
    v_read, f_read = OBJFileHandler.read(filename)
    assert len(v_read) == 3
    assert len(f_read) == 1
    assert v_read[1].x == 1.0

def test_off_io(sample_mesh_data, tmp_path):
    vertices, faces = sample_mesh_data
    filename = str(tmp_path / "test.off")
    OFFFileHandler.write(filename, vertices, faces)
    
    v_read, f_read = OFFFileHandler.read(filename)
    assert len(v_read) == 3
    assert len(f_read) == 1

def test_stl_ascii_io(sample_mesh_data, tmp_path):
    vertices, faces = sample_mesh_data
    filename = str(tmp_path / "test_ascii.stl")
    STLFileHandler.write(filename, vertices, faces, binary=False)
    
    v_read, f_read = STLFileHandler.read(filename)
    assert len(v_read) == 3
    assert len(f_read) == 1

def test_stl_binary_io(sample_mesh_data, tmp_path):
    vertices, faces = sample_mesh_data
    filename = str(tmp_path / "test_bin.stl")
    STLFileHandler.write(filename, vertices, faces, binary=True)
    
    v_read, f_read = STLFileHandler.read(filename)
    assert len(v_read) == 3
    assert len(f_read) == 1

def test_ply_ascii_io(sample_mesh_data, tmp_path):
    vertices, faces = sample_mesh_data
    filename = str(tmp_path / "test_ascii.ply")
    PLYFileHandler.write(filename, vertices, faces, binary=False)
    
    v_read, f_read = PLYFileHandler.read(filename)
    assert len(v_read) == 3
    assert len(f_read) == 1

def test_ply_binary_io(sample_mesh_data, tmp_path):
    vertices, faces = sample_mesh_data
    filename = str(tmp_path / "test_bin.ply")
    PLYFileHandler.write(filename, vertices, faces, binary=True)
    
    v_read, f_read = PLYFileHandler.read(filename)
    assert len(v_read) == 3
    assert len(f_read) == 1

def test_unified_importer_exporter(sample_mesh_data, tmp_path):
    vertices, faces = sample_mesh_data
    filename = str(tmp_path / "test_unified.obj")
    MeshExporter.write(filename, vertices, faces)
    
    v_read, f_read = MeshImporter.read(filename)
    assert len(v_read) == 3
