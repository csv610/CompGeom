from __future__ import annotations
from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, List, Dict, Optional, Tuple, Set, TYPE_CHECKING
from collections import defaultdict

from compgeom.mesh.mesh_geometry import MeshGeometry
from compgeom.mesh.mesh_topology import MeshTopology
from compgeom.mesh.algorithms.mesh_components import MeshComponents
from compgeom.mesh.surface.manifold_repair import ManifoldValidator
from compgeom.mesh.surface.mesh_queries import MeshQueries
from compgeom.kernel import Point3D

if TYPE_CHECKING:
    from compgeom.mesh.mesh import Mesh

@dataclass
class MeshInformation:
    mesh: Any
    
    # Basic Counts
    n_nodes: int = 0
    n_edges: int = 0
    n_faces: int = 0
    n_cells: int = 0
    
    # Element Types
    n_tri: int = 0
    n_quad: int = 0
    n_poly: int = 0
    
    # Topology
    n_components: int = 0
    euler_characteristic: int = 0
    genus: float = 0.0
    is_watertight: bool = False
    is_orientable: bool = False
    is_oriented: bool = False
    
    # Manifoldness / Quality
    is_manifold: bool = False
    nm_edges: List[Any] = field(default_factory=list)
    nm_verts: List[Any] = field(default_factory=list)
    comb_deg: List[Any] = field(default_factory=list)
    geom_deg: List[Any] = field(default_factory=list)
    dup_faces: List[Any] = field(default_factory=list)
    self_intersect: Any = "Unknown"
    is_solid: bool = False
    
    # Geometry
    centroid: Any = None
    bbox: Any = None
    area: float = 0.0
    volume: float = 0.0
    is_3d: bool = False
    dims: Tuple[float, ...] = field(default_factory=tuple)

    def compute(self, parallel: bool = True):
        topo = MeshTopology(self.mesh)
        # Pre-build topology to ensure thread-safety if using ThreadPoolExecutor
        topo.get_edges() 
        
        validator = ManifoldValidator(self.mesh)
        
        self.n_nodes = self.mesh.num_nodes()
        self.n_faces = self.mesh.num_faces()
        self.n_cells = self.mesh.num_cells()
        self.is_3d = isinstance(self.mesh.vertices[0], Point3D) if self.mesh.vertices else False

        tasks = {
            "face_comps": lambda: len(MeshComponents.identify_face_components(self.mesh)),
            "chi": lambda: topo.euler_characteristic(),
            "genus": lambda: topo.genus(),
            "closed": lambda: topo.is_watertight(),
            "orientable": lambda: topo.is_orientable(),
            "oriented": lambda: topo.is_oriented(),
            "nm_edges": lambda: validator.find_non_manifold_edges(),
            "nm_verts": lambda: validator.find_non_manifold_vertices(),
            "comb_deg": lambda: validator.find_combinatorial_degenerate(),
            "geom_deg": lambda: validator.find_geometric_degenerate(),
            "dup_faces": lambda: validator.find_duplicate_faces(),
            "self_intersect": self._check_self_intersection,
            "centroid": lambda: MeshGeometry.centroid(self.mesh),
            "bbox": lambda: MeshGeometry.bounding_box(self.mesh),
            "area": lambda: MeshGeometry.surface_area(self.mesh),
            "volume": lambda: MeshGeometry.volume(self.mesh) if self.is_3d else 0.0,
            "element_types": self._count_element_types,
        }

        if parallel:
            with ThreadPoolExecutor() as executor:
                future_to_task = {executor.submit(func): name for name, func in tasks.items()}
                results = {}
                for future in as_completed(future_to_task):
                    results[future_to_task[future]] = future.result()
        else:
            results = {name: func() for name, func in tasks.items()}

        self.n_edges = len(topo.get_edges())
        self.n_components = results["face_comps"]
        self.euler_characteristic = results["chi"]
        self.genus = results["genus"]
        self.is_watertight = results["closed"]
        self.is_orientable = results["orientable"]
        self.is_oriented = results["oriented"]
        self.nm_edges = results["nm_edges"]
        self.nm_verts = results["nm_verts"]
        self.comb_deg = results["comb_deg"]
        self.geom_deg = results["geom_deg"]
        self.dup_faces = results["dup_faces"]
        self.self_intersect = results["self_intersect"]
        self.centroid = results["centroid"]
        self.bbox = results["bbox"]
        self.area = results["area"]
        self.volume = results["volume"]
        
        types = results["element_types"]
        self.n_tri = types[0]
        self.n_quad = types[1]
        self.n_poly = types[2]

        self.is_manifold = (len(self.nm_edges) == 0 and len(self.nm_verts) == 0)
        self.is_solid = (self.is_watertight and self.is_manifold and self.is_oriented)

        if self.bbox:
            if self.is_3d:
                self.dims = (
                    self.bbox[1][0] - self.bbox[0][0],
                    self.bbox[1][1] - self.bbox[0][1],
                    self.bbox[1][2] - self.bbox[0][2],
                )
            else:
                self.dims = (self.bbox[1][0] - self.bbox[0][0], self.bbox[1][1] - self.bbox[0][1])

    def _check_self_intersection(self):
        try:
            intersections = MeshQueries.mesh_intersection(self.mesh, self.mesh)
            # Filter out identical faces and adjacent faces
            for f1, f2 in intersections:
                if f1 == f2: continue
                v1 = set(self.mesh.faces[f1].v_indices)
                v2 = set(self.mesh.faces[f2].v_indices)
                if len(v1 & v2) >= 2: continue # Adjacent faces share an edge
                return True
            return False
        except Exception:
            return "Unknown"

    def _count_element_types(self):
        n_tri = 0
        n_quad = 0
        n_poly = 0
        if self.mesh.num_faces() > 0:
            for face in self.mesh.faces:
                n_v = len(face)
                if n_v == 3:
                    n_tri += 1
                elif n_v == 4:
                    n_quad += 1
                else:
                    n_poly += 1
        return n_tri, n_quad, n_poly
