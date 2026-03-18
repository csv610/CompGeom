"""Triangle mesh algorithms (Delaunay and others)."""

from compgeom.mesh.surfmesh.trimesh.trimesh import TriMesh
from compgeom.mesh.surfmesh.trimesh.delaunay_triangulation import (
    DelaunayMesher,
    triangulate,
    DTriangle,
    MeshTriangle,
)
from compgeom.mesh.surfmesh.trimesh.delaunay_dc import triangulate_divide_and_conquer, DivideAndConquerDelaunayMesher
from compgeom.mesh.surfmesh.trimesh.delaunay_dynamic import DynamicDelaunay
from compgeom.mesh.surfmesh.trimesh.delaunay_constrained import constrained_delaunay_triangulation
from compgeom.mesh.surfmesh.trimesh.delaunay_topology import (
    build_topology,
    is_delaunay,
    get_nondelaunay_triangles,
)
from compgeom.mesh.surfmesh.platonic_solids import PlatonicSolid
from compgeom.mesh.surfmesh.primitives import Primitives
from compgeom.mesh.surfmesh.trimesh.domain_mesher import DomainMesher
from compgeom.mesh.surfmesh.node_move_constraints import VertexConstraint

__all__ = [
    "TriMesh",
    "DelaunayMesher",
    "triangulate",
    "DTriangle",
    "MeshTriangle",
    "triangulate_divide_and_conquer",
    "DivideAndConquerDelaunayMesher",
    "DynamicDelaunay",
    "constrained_delaunay_triangulation",
    "build_topology",
    "is_delaunay",
    "get_nondelaunay_triangles",
    "PlatonicSolid",
    "Primitives",
    "DomainMesher",
    "VertexConstraint",
]
