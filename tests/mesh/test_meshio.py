
import os
import pytest
from compgeom.kernel import Point3D
from compgeom.mesh.mesh import PolygonMesh, TriMesh
from compgeom.mesh import meshio

@pytest.fixture
def cube_mesh():
    # Standard unit cube
    vertices = [
        Point3D(0, 0, 0), Point3D(1, 0, 0), Point3D(1, 1, 0), Point3D(0, 1, 0),
        Point3D(0, 0, 1), Point3D(1, 0, 1), Point3D(1, 1, 1), Point3D(0, 1, 1)
    ]
    # 6 quad faces
    faces = [
        (0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4),
        (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)
    ]
    return PolygonMesh(vertices, faces)

@pytest.fixture
def tri_cube_mesh():
    # A cube with triangle faces
    vertices = [
        Point3D(0, 0, 0), Point3D(1, 0, 0), Point3D(1, 1, 0), Point3D(0, 1, 0),
        Point3D(0, 0, 1), Point3D(1, 0, 1), Point3D(1, 1, 1), Point3D(0, 1, 1)
    ]
    # Each quad face split into 2 triangles
    faces = [
        (0, 3, 2), (0, 2, 1), (4, 5, 6), (4, 6, 7),
        (0, 1, 5), (0, 5, 4), (1, 2, 6), (1, 6, 5),
        (2, 3, 7), (2, 7, 6), (3, 0, 4), (3, 4, 7)
    ]
    return TriMesh(vertices, faces)

def test_obj_roundtrip(cube_mesh, tmp_path):
    filename = str(tmp_path / "test.obj")
    meshio.OBJFileHandler.write(filename, cube_mesh)
    imported = meshio.OBJFileHandler.read(filename)
    
    assert len(imported.vertices) == len(cube_mesh.vertices)
    assert len(imported.faces) == len(cube_mesh.faces)
    # Check one vertex coord
    assert imported.vertices[1].x == pytest.approx(1.0)

def test_off_roundtrip(cube_mesh, tmp_path):
    filename = str(tmp_path / "test.off")
    meshio.OFFFileHandler.write(filename, cube_mesh)
    imported = meshio.OFFFileHandler.read(filename)
    
    assert len(imported.vertices) == len(cube_mesh.vertices)
    assert len(imported.faces) == len(cube_mesh.faces)

def test_stl_ascii_roundtrip(tri_cube_mesh, tmp_path):
    filename = str(tmp_path / "test_ascii.stl")
    meshio.STLFileHandler.write(filename, tri_cube_mesh, binary=False)
    imported = meshio.STLFileHandler.read(filename)
    
    # STL usually de-duplicates or separates vertices.
    # The handler uses a v_map to de-duplicate.
    assert len(imported.vertices) == 8
    assert len(imported.faces) == 12

def test_stl_binary_roundtrip(tri_cube_mesh, tmp_path):
    filename = str(tmp_path / "test_bin.stl")
    meshio.STLFileHandler.write(filename, tri_cube_mesh, binary=True)
    imported = meshio.STLFileHandler.read(filename)
    
    assert len(imported.vertices) == 8
    assert len(imported.faces) == 12

def test_ply_ascii_roundtrip(cube_mesh, tmp_path):
    filename = str(tmp_path / "test_ascii.ply")
    meshio.PLYFileHandler.write(filename, cube_mesh, binary=False)
    imported = meshio.PLYFileHandler.read(filename)
    
    assert len(imported.vertices) == 8
    assert len(imported.faces) == 6

def test_ply_binary_roundtrip(cube_mesh, tmp_path):
    filename = str(tmp_path / "test_bin.ply")
    meshio.PLYFileHandler.write(filename, cube_mesh, binary=True)
    imported = meshio.PLYFileHandler.read(filename)
    
    assert len(imported.vertices) == 8
    assert len(imported.faces) == 6

def test_unified_io(cube_mesh, tmp_path):
    filename = str(tmp_path / "cube.obj")
    meshio.to_file(filename, cube_mesh)
    assert os.path.exists(filename)
    
    imported = meshio.from_file(filename)
    assert len(imported.vertices) == 8

def test_importer_exporter_classes(cube_mesh, tmp_path):
    exporter = meshio.MeshExporter(cube_mesh)
    filename = str(tmp_path / "export.off")
    exporter.export(filename)
    
    mesh = meshio.MeshImporter.read(filename)
    assert len(mesh.faces) == 6

def test_errors():
    with pytest.raises(FileNotFoundError):
        meshio.OBJFileHandler.read("non_existent.obj")
    
    with pytest.raises(ValueError, match="Unsupported file format"):
        meshio.to_file("test.unknown", [])
        
    with pytest.raises(TypeError):
        exporter = meshio.MeshExporter()
        exporter.mesh = "not a mesh" # type: ignore
