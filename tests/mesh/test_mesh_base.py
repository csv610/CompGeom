import pytest
from compgeom.kernel import Point2D
from compgeom.mesh.mesh_base import MeshNode, MeshEdge, MeshFace, MeshCell
from compgeom.mesh.mesh import TriMesh


def test_mesh_node():
    p = Point2D(1, 2)
    node = MeshNode(id=10, point=p, attributes={"color": "red"})
    assert node.id == 10
    assert node.point == p
    assert node.attributes["color"] == "red"


def test_mesh_edge():
    # Test vertex index sorting
    e1 = MeshEdge(id=0, v_indices=(5, 2))
    assert e1.v_indices == (2, 5)

    e2 = MeshEdge(id=1, v_indices=(3, 8))
    assert e2.v_indices == (3, 8)


def test_mesh_face():
    f = MeshFace(id=5, v_indices=(0, 1, 2))
    assert len(f) == 3
    assert f[1] == 1
    assert list(f) == [0, 1, 2]


def test_mesh_cell():
    c = MeshCell(id=1, v_indices=(0, 1, 2, 3))
    assert len(c) == 4
    assert c[2] == 2
    assert list(c) == [0, 1, 2, 3]


def test_mesh_abstract_via_trimesh():
    v = [Point2D(0, 0), Point2D(1, 0), Point2D(0, 1)]
    f = [(0, 1, 2)]
    m = TriMesh(v, f)

    assert len(m.nodes) == 3
    assert len(m.vertices) == 3
    assert len(m.faces) == 1
    assert len(m.edges) == 0  # TriMesh doesn't auto-populate edges
    assert len(m.cells) == 0


def test_mesh_to_file(tmp_path):
    v = [Point2D(0, 0), Point2D(1, 0), Point2D(0, 1)]
    f = [(0, 1, 2)]
    m = TriMesh(v, f)

    path = str(tmp_path / "test.obj")
    m.to_file(path)


def test_mesh_num_queries():
    from compgeom.mesh.mesh_base import MeshFace, MeshCell

    v = [Point2D(0, 0), Point2D(1, 0), Point2D(0, 1), Point2D(1, 1)]
    f = [(0, 1, 2), (1, 3, 2)]
    m = TriMesh(v, f)

    assert m.num_nodes() == 4
    assert m.num_faces() == 2
    assert m.num_edges() == 0  # not populated by default
    assert m.num_cells() == 0


def test_mesh_with_cells():
    from compgeom.mesh.mesh_topology import MeshTopology
    from compgeom.mesh.mesh_base import MeshCell

    # Use a volume mesh class that supports cells
    from compgeom.mesh.mesh import TetMesh
    from compgeom.kernel import Point3D

    nodes = [Point3D(0, 0, 0), Point3D(1, 0, 0), Point3D(0, 1, 0), Point3D(0, 0, 1)]
    cells = [MeshCell(0, (0, 1, 2, 3))]
    m = TetMesh(nodes=nodes, cells=cells)

    assert m.num_nodes() == 4
    assert m.num_cells() == 1

    # Extract faces from cells, then edges from faces
    faces = MeshTopology.extract_faces(cells)
    edges = MeshTopology.extract_edges(faces)
    assert len(faces) == 4  # 4 faces in a tetrahedron
    assert len(edges) == 6  # 6 edges in a tetrahedron
