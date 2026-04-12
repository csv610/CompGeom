import argparse
import pathlib

import numpy as np
import pyvista as pv

from compgeom.mesh import meshio
from compgeom.mesh.meshio import OFFFileHandler, PolygonMesh


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Visualize a 3D mesh using PyVista.")
    parser.add_argument("file", help="Path to the mesh file (e.g., .off, .obj, .stl).")
    parser.add_argument("--edges", action="store_true", help="Show mesh edges.")
    parser.add_argument(
        "--nodes", action="store_true", help="Show mesh nodes (vertices)."
    )
    parser.add_argument(
        "--point-cloud",
        action="store_true",
        help="Force render as point cloud (if no faces/edges, detected automatically).",
    )
    parser.add_argument(
        "--point-size",
        type=float,
        default=5.0,
        help="Size of the points when --nodes is used.",
    )

    args = parser.parse_args(argv)

    file_path = pathlib.Path(args.file)
    ext = file_path.suffix.lower()

    if ext == ".off":
        try:
            mesh = OFFFileHandler.read(args.file)
            if isinstance(mesh, PolygonMesh) and mesh.faces:
                has_polygon_face = any(len(f.v_indices) != 3 for f in mesh.faces)
                if has_polygon_face:
                    vertices = [[v.x, v.y, getattr(v, "z", 0.0)] for v in mesh.vertices]
                    vertices_arr = np.array(vertices, dtype=np.float64)
                    faces_flat = []
                    for face in mesh.faces:
                        indices = list(face.v_indices)
                        if len(indices) == 3:
                            faces_flat.extend([3, *indices])
                        else:
                            for i in range(1, len(indices) - 1):
                                faces_flat.extend(
                                    [3, indices[0], indices[i], indices[i + 1]]
                                )
                    faces_arr = np.array(faces_flat, dtype=np.int64)
                    pv_mesh = pv.PolyData(vertices_arr, faces=faces_arr)
                else:
                    pv_mesh = pv.read(args.file)
            else:
                pv_mesh = pv.read(args.file)
        except Exception:
            pv_mesh = pv.read(args.file)
    else:
        pv_mesh = pv.read(args.file)
    if pv_mesh.n_cells == 0 and pv_mesh.n_points > 0:
        try:
            compgeom_mesh = meshio.from_file(args.file)
            vertices = [
                [v.x, v.y, getattr(v, "z", 0.0)] for v in compgeom_mesh.vertices
            ]
            vertices_arr = np.array(vertices, dtype=np.float64)
            if compgeom_mesh.faces:
                faces_flat = []
                for f in compgeom_mesh.faces:
                    faces_flat.append(len(f.v_indices))
                    faces_flat.extend(f.v_indices)
                faces_arr = np.array(faces_flat, dtype=np.int64)
                pv_mesh = pv.PolyData(vertices_arr, faces=faces_arr)
            elif compgeom_mesh.edges:
                edges_flat = []
                for e in compgeom_mesh.edges:
                    edges_flat.extend([2, e.v_indices[0], e.v_indices[1]])
                edges_arr = np.array(edges_flat, dtype=np.int64)
                pv_mesh = pv.PolyData(vertices_arr, lines=edges_arr)
        except Exception:
            pass

    mesh = pv_mesh

    plotter = pv.Plotter()
    plotter.set_background("black")
    plotter.enable_anti_aliasing("msaa", multi_samples=8)

    has_faces = False
    has_lines = False

    if isinstance(mesh, pv.PolyData):
        has_lines = mesh.n_lines > 0
        try:
            has_faces = mesh.n_faces_strict > 0
        except AttributeError:
            has_faces = False
    elif hasattr(mesh, "n_cells"):
        if mesh.n_cells > 0:
            cell_types = set(mesh.GetCellType(i) for i in range(min(mesh.n_cells, 100)))
            has_faces = any(ct in (5, 6, 7, 8, 9) for ct in cell_types)

    is_point_cloud = args.point_cloud or (
        not has_faces and not has_lines and mesh.n_points > 0 and mesh.n_cells == 0
    )

    if is_point_cloud:
        plotter.add_points(
            mesh.points,
            color="lightblue",
            point_size=args.point_size,
            render_points_as_spheres=False,
        )
    elif has_lines:
        plotter.add_mesh(
            mesh, show_edges=args.edges, color="lightblue", opacity=0.8, lighting=False
        )
    else:
        plotter.add_mesh(mesh, show_edges=args.edges, color="lightblue", opacity=0.8)

    show_edges = args.edges
    show_nodes = args.nodes

    sphere_radius = args.point_size * 0.02
    node_actor = None
    if show_nodes:
        sphere = pv.Sphere(radius=sphere_radius, theta_resolution=8, phi_resolution=8)
        node_mesh = mesh.points.glyph(scale=False, geom=sphere, orient=False)
        node_actor = plotter.add_mesh(
            node_mesh, color="red", smooth_shading=True, lighting=False
        )

    mesh_actor = None
    for actor in plotter.actors.values():
        if hasattr(actor, "mapper") and hasattr(actor.mapper, "SetInput"):
            mesh_actor = actor
            break

    def toggle_edges():
        nonlocal show_edges
        show_edges = not show_edges
        if mesh_actor:
            mesh_actor.GetProperty().SetEdgeVisibility(show_edges)
        plotter.render()

    def toggle_nodes():
        nonlocal show_nodes, node_actor
        show_nodes = not show_nodes
        if node_actor:
            node_actor.SetVisibility(show_nodes)
        elif show_nodes:
            sphere = pv.Sphere(
                radius=sphere_radius, theta_resolution=8, phi_resolution=8
            )
            node_mesh = mesh.points.glyph(scale=False, geom=sphere, orient=False)
            node_actor = plotter.add_mesh(
                node_mesh, color="red", smooth_shading=True, lighting=False
            )
        else:
            node_actor = None

    def set_mesh_representation(rep_type: str):
        if mesh_actor:
            if rep_type == "wireframe":
                mesh_actor.GetProperty().SetRepresentationToWireframe()
            elif rep_type == "surface":
                mesh_actor.GetProperty().SetRepresentationToSurface()
        plotter.render()

    plotter.add_key_event("e", toggle_edges)
    plotter.add_key_event("v", toggle_nodes)
    plotter.add_key_event("w", lambda: set_mesh_representation("wireframe"))
    plotter.add_key_event("s", lambda: set_mesh_representation("surface"))
    plotter.add_key_event("r", plotter.reset_camera)
    plotter.add_key_event("q", plotter.close)

    print("Interactive keys in the viewer:")
    print("  'e' - Toggle edges")
    print("  'v' - Toggle vertices (nodes)")
    print("  'w' - Switch to wireframe")
    print("  's' - Switch to surface")
    print("  'r' - Reset camera")
    print("  'q' - Quit viewer")

    plotter.show()
    return 0


if __name__ == "__main__":
    main()
