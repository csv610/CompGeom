
import math
import pytest
from compgeom.kernel import Point3D
from compgeom.mesh.surface.trimesh.trimesh import TriMesh
from compgeom.mesh.surface.node_move_constraints import VertexConstraint

def test_project_to_line():
    p = Point3D(5, 5, 5)
    s, e = Point3D(0, 0, 0), Point3D(10, 0, 0)
    res = VertexConstraint.project_to_line(p, s, e)
    assert res == Point3D(5, 0, 0)
    
    # Point at the start
    res2 = VertexConstraint.project_to_line(s, s, e)
    assert res2 == s

def test_project_to_sphere():
    center = Point3D(0, 0, 0)
    radius = 10.0
    p = Point3D(20, 0, 0)
    res = VertexConstraint.project_to_sphere(p, center, radius)
    assert res == Point3D(10, 0, 0)
    
    # Point inside
    p2 = Point3D(5, 0, 0)
    res2 = VertexConstraint.project_to_sphere(p2, center, radius)
    assert res2 == Point3D(10, 0, 0)

def test_project_to_ellipsoid():
    center = Point3D(0, 0, 0)
    p = Point3D(10, 0, 0)
    # Ellipsoid with rx=5, ry=2, rz=2
    res = VertexConstraint.project_to_ellipsoid(p, center, 5, 2, 2)
    # The current implementation projects along the ray from center.
    # For (10,0,0), the intersection with x^2/25 + y^2/4 + z^2/4 = 1 is (5,0,0)
    assert res == Point3D(5, 0, 0)

def test_project_to_cuboid():
    min_c, max_c = Point3D(0, 0, 0), Point3D(10, 10, 10)
    
    # Outside point
    p_out = Point3D(15, 5, 5)
    assert VertexConstraint.project_to_cuboid(p_out, min_c, max_c) == Point3D(10, 5, 5)
    
    # Inside point (should project to nearest face)
    p_in = Point3D(1, 5, 5)
    # nearest to min_x=0
    assert VertexConstraint.project_to_cuboid(p_in, min_c, max_c) == Point3D(0, 5, 5)

def test_project_to_cylinder():
    bottom, top = Point3D(0, 0, 0), Point3D(0, 0, 10)
    radius = 5.0
    
    # Outside on side
    p1 = Point3D(10, 0, 5)
    assert VertexConstraint.project_to_cylinder(p1, bottom, top, radius) == Point3D(5, 0, 5)
    
    # Above top cap
    p2 = Point3D(0, 0, 15)
    assert VertexConstraint.project_to_cylinder(p2, bottom, top, radius) == Point3D(0, 0, 10)
    
    # Inside cylinder
    p3 = Point3D(1, 0, 5)
    # Distances: side=4, bottom=5, top=5. Should project to side.
    res3 = VertexConstraint.project_to_cylinder(p3, bottom, top, radius)
    assert res3 == Point3D(5, 0, 5)

def test_project_to_mesh():
    # Simple triangle at z=0
    v = [Point3D(0,0,0), Point3D(10,0,0), Point3D(0,10,0)]
    f = [(0,1,2)]
    mesh = TriMesh(v, f)
    
    # Point above
    p = Point3D(2, 2, 5)
    res = VertexConstraint.project_to_mesh(p, mesh)
    assert res == Point3D(2, 2, 0)
    
    # Point far outside
    p2 = Point3D(20, 20, 0)
    res2 = VertexConstraint.project_to_mesh(p2, mesh)
    # Should project to the hypotenuse
    assert res2.x == pytest.approx(5.0)
    assert res2.y == pytest.approx(5.0)
    assert res2.z == 0
