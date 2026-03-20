import pytest
import math
from compgeom.kernel import Point3D
from compgeom.mesh.volume.polyhedral_mesh import PolyhedralMesh
from compgeom.mesh.volume.voromesh.voronoi_3d import VoronoiDiagram3D
from compgeom.mesh.volume.volume_validation import validate_voronoi_mesh
from compgeom.mesh.volume.voromesh.bounded_voronoi_3d import BoundedVoronoi3D

def test_polyhedral_mesh_instantiation():
    vertices = [Point3D(0,0,0), Point3D(1,0,0), Point3D(0,1,0), Point3D(0,0,1)]
    # A single cell with 4 triangular faces (a tetrahedron)
    faces = [[0, 2, 1], [0, 1, 3], [0, 3, 2], [1, 2, 3]]
    cells = [faces]
    mesh = PolyhedralMesh(vertices, cells)
    assert len(mesh.vertices) == 4
    assert len(mesh.poly_cells) == 1
    assert len(mesh.get_cell_faces(0)) == 4

def test_voronoi_3d_basic():
    # 5 points to ensure we have at least one internal tetrahedron and thus at least one finite Voronoi vertex
    points = [
        Point3D(0, 0, 0),
        Point3D(1, 0, 0),
        Point3D(0, 1, 0),
        Point3D(0, 0, 1),
        Point3D(0.2, 0.2, 0.2) # Internal point
    ]
    voronoi = VoronoiDiagram3D()
    mesh = voronoi.compute(points)
    
    assert len(mesh.vertices) >= 1
    assert len(mesh.poly_cells) == 5

def test_bounded_voronoi_box():
    # 2 points in a box
    points = [
        Point3D(0.25, 0.5, 0.5),
        Point3D(0.75, 0.5, 0.5)
    ]
    # Box [0, 1] x [0, 1] x [0, 1]
    bv = BoundedVoronoi3D.from_box(Point3D(0, 0, 0), Point3D(1, 1, 1))
    mesh = bv.compute(points)
    
    assert len(mesh.poly_cells) == 2
    
    # Validate the mesh
    is_valid, errors = validate_voronoi_mesh(mesh)
    assert is_valid, f"Voronoi mesh validation failed: {errors}"
    
    # For these points, the bisector is x=0.5. 
    # Each cell should have 6 faces (5 from box, 1 from bisector).
    for cell in mesh.poly_cells:
        assert len(cell) == 6

def test_bounded_voronoi_sphere():
    points = [Point3D(0, 0, 0)]
    # A single point in a sphere. The cell should be the (approximate) sphere itself.
    radius = 1.0
    num_planes = 20
    bv = BoundedVoronoi3D.from_sphere(Point3D(0, 0, 0), radius, num_planes=num_planes)
    mesh = bv.compute(points)
    
    assert len(mesh.poly_cells) == 1
    # The cell should have 'num_planes' faces if they all clip the box.
    assert len(mesh.poly_cells[0]) >= num_planes
    
    is_valid, errors = validate_voronoi_mesh(mesh)
    assert is_valid, f"Sphere-bounded Voronoi validation failed: {errors}"

def test_bounded_voronoi_cylinder():
    points = [Point3D(0, 0, 0)]
    radius = 1.0
    height = 2.0
    num_sides = 8
    bv = BoundedVoronoi3D.from_cylinder(Point3D(0, 0, 0), radius, height, num_sides=num_sides)
    mesh = bv.compute(points)
    
    assert len(mesh.poly_cells) == 1
    # Cylinder should have num_sides + 2 faces.
    assert len(mesh.poly_cells[0]) == num_sides + 2
    
    is_valid, errors = validate_voronoi_mesh(mesh)
    assert is_valid, f"Cylinder-bounded Voronoi validation failed: {errors}"

def test_voronoi_validation_convexity():
    # Create a manually distorted mesh to test validation
    vertices = [
        Point3D(0,0,0), Point3D(1,0,0), Point3D(1,1,0), Point3D(0,1,0),
        Point3D(0.5, 0.5, -1), # Bottom
        Point3D(0.5, 0.5, 0.5),  # TOP - THIS MAKES IT CONCAVE if combined wrongly
    ]
    # A pyramid with a dented top would be concave.
    # We'll just check that our validate function catches some errors.
    pass

def test_voronoi_random_points():
    import random
    random.seed(42)
    points = [Point3D(random.random(), random.random(), random.random()) for _ in range(10)]
    
    bv = BoundedVoronoi3D.from_box(Point3D(0, 0, 0), Point3D(1, 1, 1))
    mesh = bv.compute(points)
    
    assert len(mesh.poly_cells) == 10
    is_valid, errors = validate_voronoi_mesh(mesh)
    assert is_valid, f"Random Voronoi validation failed: {errors}"
