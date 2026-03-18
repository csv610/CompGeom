import unittest
import math
from compgeom.mesh import (
    MeshNode, MeshEdge, MeshFace, MeshCell, MeshAffineTransform, MeshGeometry, MeshProcessing,
    TriMesh, QuadMesh, PolygonMesh, TetMesh, HexMesh, MeshTopology
)
from compgeom.kernel import Point2D, Point3D

class TestMeshDatastructures(unittest.TestCase):
    def test_mesh_node(self):
        p = Point2D(1.0, 2.0)
        node = MeshNode(0, p, {"color": "red"})
        self.assertEqual(node.id, 0)
        self.assertEqual(node.point, p)
        self.assertEqual(node.attributes["color"], "red")

    def test_mesh_edge_sorting(self):
        # MeshEdge ensures v_indices are sorted
        e1 = MeshEdge(0, (1, 2))
        self.assertEqual(e1.v_indices, (1, 2))
        e2 = MeshEdge(1, (2, 1))
        self.assertEqual(e2.v_indices, (1, 2))

class TestTriMesh(unittest.TestCase):
    def setUp(self):
        # A simple triangle: (0,0), (1,0), (0,1)
        self.points = [Point2D(0, 0), Point2D(1, 0), Point2D(0, 1)]
        self.faces = [(0, 1, 2)]
        self.mesh = TriMesh(self.points, self.faces)

    def test_basic_properties(self):
        self.assertEqual(len(self.mesh.nodes), 3)
        self.assertEqual(len(self.mesh.faces), 1)
        self.assertEqual(len(self.mesh.vertices), 3)

    def test_centroid(self):
        c = MeshGeometry.centroid(self.mesh)
        self.assertAlmostEqual(c.x, 1/3)
        self.assertAlmostEqual(c.y, 1/3)

    def test_bounding_box(self):
        bbox = MeshGeometry.bounding_box(self.mesh)
        self.assertEqual(bbox, ((0.0, 0.0), (1.0, 1.0)))

    def test_transformations(self):
        # Translate
        MeshAffineTransform.translate(self.mesh, 1.0, 2.0)
        self.assertAlmostEqual(self.mesh.nodes[0].point.x, 1.0)
        self.assertAlmostEqual(self.mesh.nodes[0].point.y, 2.0)
        
        # Scale
        MeshAffineTransform.scale(self.mesh, 2.0, 3.0)
        # nodes[0] was at (1,2), now should be (2,6)
        self.assertAlmostEqual(self.mesh.nodes[0].point.x, 2.0)
        self.assertAlmostEqual(self.mesh.nodes[0].point.y, 6.0)

    def test_flip_normals(self):
        # Initial face: (0, 1, 2)
        self.assertEqual(self.mesh.faces[0].v_indices, (0, 1, 2))
        
        # Flip normals
        MeshProcessing.flip_normals(self.mesh)
        
        # New face should be (2, 1, 0)
        self.assertEqual(self.mesh.faces[0].v_indices, (2, 1, 0))

    def test_euler_characteristic(self):
        # V=3, E=3, F=1 -> 3 - 3 + 1 = 1
        self.assertEqual(self.mesh.euler_characteristic(), 1)

    def test_is_watertight(self):
        # A single triangle is not watertight
        self.assertFalse(MeshTopology(self.mesh).is_watertight())
        
        # A tetrahedron is watertight
        pts = [Point3D(0,0,0), Point3D(1,0,0), Point3D(0,1,0), Point3D(0,0,1)]
        faces = [(0,1,2), (0,2,3), (0,3,1), (1,3,2)]
        tet = TriMesh(pts, faces)
        self.assertTrue(MeshTopology(tet).is_watertight())

class TestMeshTopology(unittest.TestCase):
    def test_topology_queries(self):
        # Two triangles sharing an edge: (0,1,2) and (1,3,2)
        # Points: 0:(0,0), 1:(1,0), 2:(0,1), 3:(1,1)
        pts = [Point2D(0,0), Point2D(1,0), Point2D(0,1), Point2D(1,1)]
        faces = [(0,1,2), (1,3,2)]
        mesh = TriMesh(pts, faces)
        topo = MeshTopology(mesh)
        
        # Vertex neighbors of 1 should be 0, 2, 3
        self.assertEqual(topo.vertex_neighbors(1), {0, 2, 3})
        
        # Vertex elements of 1 should be both triangles (0 and 1)
        self.assertEqual(topo.vertex_elements(1), {0, 1})
        
        # Element neighbors of face 0 should be face 1
        self.assertEqual(topo.element_neighbors(0), {1})
        
        # Shared edge neighbors of face 0 should be face 1
        self.assertEqual(topo.shared_edge_neighbors(0), {1})
        
        # Boundary edges: (0,1), (0,2), (1,3), (3,2)
        # (1,2) is shared
        boundaries = topo.boundary_edges()
        self.assertEqual(len(boundaries), 4)
        sorted_boundaries = sorted([tuple(sorted(e)) for e in boundaries])
        self.assertEqual(sorted_boundaries, [(0, 1), (0, 2), (1, 3), (2, 3)])

class TestQuadMesh(unittest.TestCase):
    def test_extract_chord(self):
        # 2x2 grid of quads
        # 0--1--2
        # | 0| 1|
        # 3--4--5
        # | 2| 3|
        # 6--7--8
        pts = [Point2D(x, y) for y in [0,1,2] for x in [0,1,2]]
        faces = [
            (0, 1, 4, 3), # Quad 0
            (1, 2, 5, 4), # Quad 1
            (3, 4, 7, 6), # Quad 2
            (4, 5, 8, 7)  # Quad 3
        ]
        mesh = QuadMesh(pts, faces)
        
        # Chord starting from quad 0, edge (0,1) which is index 0
        # Edge 0 is top. Opposite is edge 2 (4,3).
        # Neighbor across edge 2 is quad 2.
        chord = mesh.extract_chord(0, 0)
        self.assertEqual(chord, [2, 0])
        
        # Chord starting from quad 0, edge (1,4) which is index 1
        # Edge 1 is right. Opposite is edge 3 (3,0).
        # Neighbor across edge 1 is quad 1.
        chord2 = mesh.extract_chord(0, 1)
        self.assertEqual(chord2, [0, 1])

class TestPolygonMesh(unittest.TestCase):
    def test_triangulate(self):
        # A single square as a polygon
        pts = [Point2D(0,0), Point2D(1,0), Point2D(1,1), Point2D(0,1)]
        faces = [(0, 1, 2, 3)]
        poly_mesh = PolygonMesh(pts, faces)
        
        tri_mesh = poly_mesh.triangulate()
        self.assertEqual(len(tri_mesh.faces), 2)
        self.assertEqual(len(tri_mesh.nodes), 4)

class TestVolMeshTopology(unittest.TestCase):
    def test_tetmesh_boundary_faces(self):
        # Two tetrahedra sharing a face (0,1,2)
        # 0:(0,0,0), 1:(1,0,0), 2:(0,1,0), 3:(0,0,1), 4:(0,0,-1)
        pts = [Point3D(0,0,0), Point3D(1,0,0), Point3D(0,1,0), Point3D(0,0,1), Point3D(0,0,-1)]
        cells = [(0,1,2,3), (0,1,2,4)]
        mesh = TetMesh(pts, cells)
        topo = MeshTopology(mesh)
        
        # Total faces per cell: 4. Shared face: (0,1,2).
        # Faces in cell 0: (0,1,2), (0,1,3), (0,2,3), (1,2,3)
        # Faces in cell 1: (0,1,2), (0,1,4), (0,2,4), (1,2,4)
        # Boundary faces: 3 from cell 0 + 3 from cell 1 = 6
        boundary_faces = topo.boundary_faces()
        self.assertEqual(len(boundary_faces), 6)
        
        # (0,1,2) should NOT be in boundary_faces
        sorted_boundary_faces = [tuple(sorted(f)) for f in boundary_faces]
        self.assertNotIn((0,1,2), sorted_boundary_faces)

    def test_tetmesh_boundary_edges(self):
        # Single tetrahedron has all 6 edges on the boundary
        pts = [Point3D(0,0,0), Point3D(1,0,0), Point3D(0,1,0), Point3D(0,0,1)]
        cells = [(0,1,2,3)]
        mesh = TetMesh(pts, cells)
        topo = MeshTopology(mesh)
        
        boundaries = topo.boundary_edges()
        self.assertEqual(len(boundaries), 6)
        
        # Two tets sharing a face (0,1,2)
        cells2 = [(0,1,2,3), (0,1,2,4)]
        pts2 = pts + [Point3D(0,0,-1)]
        mesh2 = TetMesh(pts2, cells2)
        # Shared edges of face (0,1,2): (0,1), (1,2), (2,0)
        # These 3 edges should NOT be in boundary_edges because they are shared by 2 elements
        topo2 = MeshTopology(mesh2)
        boundaries2 = topo2.boundary_edges()
        # 6 (non-shared edges) = 6 boundary edges
        self.assertEqual(len(boundaries2), 6)
        sorted_boundaries2 = [tuple(sorted(e)) for e in boundaries2]
        self.assertNotIn((0,1), sorted_boundaries2)
        self.assertNotIn((1,2), sorted_boundaries2)
        self.assertNotIn((0,2), sorted_boundaries2)

    def test_hexmesh_boundary_faces(self):
        # Two hexahedra sharing a face (4,5,6,7)
        # Hex 0: 0,1,2,3 (bottom), 4,5,6,7 (top)
        # Hex 1: 4,5,7,6 (bottom), 8,9,11,10 (top)
        # Standard VTK: 0-1-2-3 bottom, 4-5-6-7 top
        pts = [Point3D(x,y,z) for z in [0,1,2] for y in [0,1] for x in [0,1]]
        cells = [
            (0, 1, 3, 2, 4, 5, 7, 6), # Hex 0
            (4, 5, 7, 6, 8, 9, 11, 10) # Hex 1
        ]
        mesh = HexMesh(pts, cells)
        topo = MeshTopology(mesh)
        
        # 2 hexes, each 6 faces. 1 shared face -> 5 + 5 = 10 boundary faces.
        boundary_faces = topo.boundary_faces()
        self.assertEqual(len(boundary_faces), 10)
        
        # Shared face (4,5,6,7) should NOT be in boundary_faces
        sorted_boundary_faces = [tuple(sorted(f)) for f in boundary_faces]
        self.assertNotIn((4,5,6,7), sorted_boundary_faces)

if __name__ == "__main__":
    unittest.main()
