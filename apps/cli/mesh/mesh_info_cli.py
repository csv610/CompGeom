from __future__ import annotations

import argparse
import sys
import math
from compgeom.mesh import meshio
from compgeom.mesh.mesh_geometry import MeshGeometry
from compgeom.mesh.mesh_topology import MeshTopology
from compgeom.mesh.algorithms.mesh_components import MeshComponents
from compgeom.mesh.surface.manifold_repair import ManifoldValidator
from compgeom.mesh.surface.mesh_queries import MeshQueries
from compgeom.algo.bounding import minimum_bounding_box
from compgeom.kernel import Point2D, Point3D


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Provide detailed information about a 3D or 2D mesh."
    )
    parser.add_argument(
        "input", help="Path to the input mesh file (OBJ, OFF, STL, PLY)."
    )

    args = parser.parse_args(argv)

    print(f"Loading mesh from {args.input}...")
    try:
        mesh = meshio.from_file(args.input)
    except Exception as e:
        print(f"Error reading mesh: {e}")
        return 1

    # Topology & Components
    topo = MeshTopology(mesh)
    validator = ManifoldValidator(mesh)
    n_nodes = mesh.num_nodes()
    n_edges = len(topo.get_edges())
    n_faces = mesh.num_faces()
    n_cells = mesh.num_cells()
    
    face_comps = MeshComponents.identify_face_components(mesh)
    n_components = len(face_comps)
    
    chi = topo.euler_characteristic()
    genus = topo.genus()
    closed = topo.is_watertight()
    orientable = topo.is_orientable()
    oriented = topo.is_oriented()
    
    nm_edges = validator.find_non_manifold_edges()
    nm_verts = validator.find_non_manifold_vertices()
    comb_deg = validator.find_combinatorial_degenerate()
    geom_deg = validator.find_geometric_degenerate()
    dup_faces = validator.find_duplicate_faces()
    
    # Self Interaction (Brute force for now if small, or use AABB)
    self_intersect = False
    if n_faces < 500: # Limit brute force
        try:
            intersections = MeshQueries.mesh_intersection(mesh, mesh)
            # Filter out identical faces and adjacent faces
            actual_intersections = []
            for f1, f2 in intersections:
                if f1 == f2: continue
                v1 = set(mesh.faces[f1].v_indices)
                v2 = set(mesh.faces[f2].v_indices)
                if len(v1 & v2) >= 2: continue # Adjacent faces share an edge
                actual_intersections.append((f1, f2))
            self_intersect = len(actual_intersections) > 0
        except Exception:
            self_intersect = "Unknown (Check Error)"
    else:
        self_intersect = "Skipped (Mesh too large)"

    is_manifold = (len(nm_edges) == 0 and len(nm_verts) == 0)
    is_solid = (closed and is_manifold and oriented and is_manifold)

    n_tri = 0
    n_quad = 0
    n_poly = 0
    if n_faces > 0:
        for face in mesh.faces:
            n_v = len(face)
            if n_v == 3:
                n_tri += 1
            elif n_v == 4:
                n_quad += 1
            else:
                n_poly += 1

    # Geometry
    centroid = MeshGeometry.centroid(mesh)
    bbox = MeshGeometry.bounding_box(mesh)
    area = MeshGeometry.surface_area(mesh)
    volume = MeshGeometry.volume(mesh)

    is_3d = isinstance(mesh.vertices[0], Point3D) if mesh.vertices else False

    print("\n--- Mesh Information ---")
    print(f"File:           {args.input}")
    print(f"Dimensions:     {'3D' if is_3d else '2D'}")
    print(f"Nodes:          {n_nodes}")
    print(f"Edges:          {n_edges}")
    if n_faces > 0:
        print(f"Faces:          {n_faces}")
        print(f"  Triangles:    {n_tri}")
        print(f"  Quads:        {n_quad}")
        print(f"  Polygons:     {n_poly}")
    if n_cells > 0:
        print(f"Cells:          {n_cells}")

    print(f"\n--- Topology & Diagnostics ---")
    print(f"Components:     {n_components}")
    print(f"Euler Char:     {chi}")
    print(f"Genus:          {genus:.1f}")
    print(f"Closed:         {'Yes' if closed else 'No'}")
    print(f"Orientable:     {'Yes' if orientable else 'No'}")
    print(f"Oriented:       {'Yes' if oriented else 'No'}")
    print(f"Vertex Manifold:{'Yes' if not nm_verts else f'No ({len(nm_verts)} bad)'}")
    print(f"Edge Manifold:  {'Yes' if not nm_edges else f'No ({len(nm_edges)} bad)'}")
    print(f"Self-Intersect: {self_intersect}")
    print(f"Comb. Degenerate: {len(comb_deg)}")
    print(f"Geom. Degenerate: {len(geom_deg)}")
    print(f"Duplicate Faces: {len(dup_faces)}")
    print(f"Solid:          {'Yes' if is_solid else 'No'}")

    print(f"\n--- Geometry ---")
    print(f"Centroid:       ({centroid.x:.4f}, {centroid.y:.4f}, {getattr(centroid, 'z', 0.0):.4f})")

    if bbox:
        print(f"Bounding Box (AABB):")
        print(f"  Min: {bbox[0]}")
        print(f"  Max: {bbox[1]}")
        if is_3d:
            dims = (
                bbox[1][0] - bbox[0][0],
                bbox[1][1] - bbox[0][1],
                bbox[1][2] - bbox[0][2],
            )
        else:
            dims = (bbox[1][0] - bbox[0][0], bbox[1][1] - bbox[0][1])
        print(f"  Size: {dims}")

    print(f"Surface Area:   {area:.6f}")
    if is_3d:
        print(f"Volume:         {volume:.6f}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
