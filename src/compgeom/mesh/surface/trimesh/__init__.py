"""Triangle mesh algorithms (Delaunay and others)."""

from compgeom.mesh.surface.trimesh.trimesh import TriMesh
from compgeom.mesh.surface.trimesh.delaunay_triangulation import (
    DelaunayMesher,
    triangulate,
    DTriangle,
    MeshTriangle,
)
from compgeom.mesh.surface.trimesh.delaunay_dc import triangulate_divide_and_conquer, DivideAndConquerDelaunayMesher
from compgeom.mesh.surface.trimesh.delaunay_dynamic import DynamicDelaunay
from compgeom.mesh.surface.trimesh.delaunay_constrained import constrained_delaunay_triangulation
from compgeom.mesh.surface.trimesh.delaunay_topology import (
    build_topology,
    is_delaunay,
    get_nondelaunay_triangles,
)
from compgeom.mesh.surface.platonic_solids import PlatonicSolid
from compgeom.mesh.surface.primitives import Primitives
from compgeom.mesh.surface.trimesh.domain_mesher import DomainMesher
from compgeom.mesh.surface.node_move_constraints import VertexConstraint

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
