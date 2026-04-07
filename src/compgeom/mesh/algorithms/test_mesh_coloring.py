import unittest
from compgeom.kernel import Point2D
from compgeom.mesh.surface.trimesh.trimesh import TriMesh
from compgeom.mesh.algorithms.mesh_coloring import MeshColoring
from compgeom.verifiers.mesh.mesh_verifiers import (
    verify_mesh_vertex_coloring,
    verify_mesh_element_coloring,
)


class TestMeshColoring(unittest.TestCase):
    def setUp(self):
        # Create a simple triangle mesh (two triangles sharing an edge)
        # 0 -- 1
        # |  / |
        # 2 -- 3
        vertices = [
            Point2D(0, 1),  # 0
            Point2D(1, 1),  # 1
            Point2D(0, 0),  # 2
            Point2D(1, 0),  # 3
        ]
        faces = [
            (0, 1, 2),  # Face 0
            (1, 3, 2),  # Face 1
        ]
        self.mesh = TriMesh(vertices, faces)

    def test_vertex_coloring(self):
        coloring = MeshColoring.color_vertices(self.mesh)
        # Verify result
        self.assertTrue(verify_mesh_vertex_coloring(self.mesh, coloring))

    def test_element_coloring(self):
        coloring = MeshColoring.color_elements(self.mesh)
        # Verify result
        self.assertTrue(verify_mesh_element_coloring(self.mesh, coloring))

    def test_invalid_vertex_coloring(self):
        coloring = MeshColoring.color_vertices(self.mesh)
        if len(coloring) > 0:
            # Manually make it invalid by giving neighbors the same color
            # Vertex 1 and 2 share an edge.
            v1, v2 = 1, 2
            coloring[v1] = coloring[v2]
            with self.assertRaises(ValueError):
                verify_mesh_vertex_coloring(self.mesh, coloring)

    def test_invalid_element_coloring(self):
        # Two faces share an edge (1, 2).
        coloring = MeshColoring.color_elements(self.mesh)
        if len(coloring) > 1:
            coloring[0] = coloring[1]
            with self.assertRaises(ValueError):
                verify_mesh_element_coloring(self.mesh, coloring)


if __name__ == "__main__":
    unittest.main()
