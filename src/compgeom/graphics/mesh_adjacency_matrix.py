"""Adjacency matrix visualization for Meshes."""

from __future__ import annotations

import argparse
import struct
import zlib
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from ..mesh.mesh import Mesh


def get_node_node_adjacency(mesh: Mesh) -> List[List[int]]:
    """Compute node-node adjacency matrix.

    A_ij = 1 if node i and node j share an edge in any element.
    """
    num_nodes = len(mesh.vertices)
    adj = [[0] * num_nodes for _ in range(num_nodes)]
    # Diagonal is set to 1 (a node is adjacent to itself)
    for i in range(num_nodes):
        adj[i][i] = 1

    for element in mesh.elements:
        for i in range(len(element)):
            v1 = element[i]
            v2 = element[(i + 1) % len(element)]
            adj[v1][v2] = 1
            adj[v2][v1] = 1
    return adj


def get_cell_node_adjacency(mesh: Mesh) -> List[List[int]]:
    """Compute cell-node adjacency matrix.

    M_ij = 1 if node j belongs to cell i.
    """
    num_nodes = len(mesh.vertices)
    num_cells = len(mesh.elements)
    adj = [[0] * num_nodes for _ in range(num_cells)]
    for cell_idx, element in enumerate(mesh.elements):
        for node_idx in element:
            adj[cell_idx][node_idx] = 1
    return adj


def save_matrix_as_png(matrix: List[List[int]], filename: str, cell_size: int = 8):
    """Save a binary matrix as a PNG image where 1 is black and 0 is white."""
    rows = len(matrix)
    cols = len(matrix[0]) if rows > 0 else 0
    if rows == 0 or cols == 0:
        return

    width = cols * cell_size
    height = rows * cell_size

    # White background (RGB: 255, 255, 255)
    img_data = bytearray([255] * (width * height * 3))

    def set_pixel(x, y, color):
        if 0 <= x < width and 0 <= y < height:
            idx = (y * width + x) * 3
            img_data[idx : idx + 3] = bytearray(color)

    for r in range(rows):
        for c in range(cols):
            if matrix[r][c]:
                # Draw a black square for non-zero entries
                color = (0, 0, 0)
                for i in range(cell_size):
                    for j in range(cell_size):
                        set_pixel(c * cell_size + i, r * cell_size + j, color)

    # PNG generation logic
    png = b"\x89PNG\r\n\x1a\n"
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    png += struct.pack(">I", 13) + b"IHDR" + ihdr + struct.pack(">I", zlib.crc32(b"IHDR" + ihdr) & 0xFFFFFFFF)

    row_bytes = []
    for y in range(height):
        # Each row starts with a filter type byte (0 for None)
        row_bytes.append(b"\x00" + bytes(img_data[y * width * 3 : (y + 1) * width * 3]))

    compressed = zlib.compress(b"".join(row_bytes))
    png += (
        struct.pack(">I", len(compressed))
        + b"IDAT"
        + compressed
        + struct.pack(">I", zlib.crc32(b"IDAT" + compressed) & 0xFFFFFFFF)
    )
    png += struct.pack(">I", 0) + b"IEND" + struct.pack(">I", zlib.crc32(b"IEND") & 0xFFFFFFFF)

    with open(filename, "wb") as f:
        f.write(png)


def get_spatial_adjacency(mesh: Mesh, eps: float = 1e-5) -> List[List[int]]:
    """Compute spatial adjacency matrix using an R-tree.

    A_ij = 1 if distance between node i and node j is less than eps.
    """
    from ..index.rtree import RTree, BoundingBox

    num_nodes = len(mesh.vertices)
    adj = [[0] * num_nodes for _ in range(num_nodes)]
    tree = RTree[int](max_entries=16)

    # Insert all points into the R-tree
    for i, p in enumerate(mesh.vertices):
        if p:
            bbox = BoundingBox.from_point(p.x, p.y, padding=0.0)
            tree.insert(bbox, i)

    # Query R-tree for each point
    for i, p in enumerate(mesh.vertices):
        if not p:
            continue
        query_bbox = BoundingBox.from_point(p.x, p.y, padding=eps)
        nearby_indices = tree.query(query_bbox)
        for j in nearby_indices:
            adj[i][j] = 1
            adj[j][i] = 1
    return adj


def visualize_adjacencies(mesh: Mesh, prefix: str = "mesh", eps: float = 1e-5):
    """Visualize node-node, cell-node, and spatial adjacency matrices."""
    node_node = get_node_node_adjacency(mesh)
    cell_node = get_cell_node_adjacency(mesh)
    spatial = get_spatial_adjacency(mesh, eps)

    save_matrix_as_png(node_node, f"{prefix}_node_node.png")
    save_matrix_as_png(cell_node, f"{prefix}_cell_node.png")
    save_matrix_as_png(spatial, f"{prefix}_spatial.png")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create node-node/cell-nodes adjacency matrix images for a given mesh.")
    parser.add_argument("filename", nargs="?", help="Input mesh file (OBJ, OFF, STL, etc.)")
    parser.add_argument("--prefix", default="mesh", help="Prefix for output images")
    args = parser.parse_args()

    if args.filename:
        # Import here to avoid circular dependency or unnecessary loading
        from ..mesh.mesh import TriangleMesh

        mesh = TriangleMesh.from_file(args.filename)
        visualize_adjacencies(mesh, args.prefix)
        print(f"Adjacency matrix images for '{args.filename}' generated.")
    else:

        class DummyMesh:
            def __init__(self, vertices, elements):
                self.vertices = vertices
                self.elements = elements

        class Point:
            def __init__(self, x, y):
                self.x = x
                self.y = y

        # A simple square divided into two triangles
        # 3 -- 2
        # | \  |
        # 0 -- 1
        points = [Point(0, 0), Point(1, 0), Point(1, 1), Point(0, 1)]
        dummy_mesh = DummyMesh(vertices=points, elements=[[0, 1, 2], [0, 2, 3]])

        visualize_adjacencies(dummy_mesh, "example", eps=1.1)
        print("No input file provided. Example images generated (node-node, cell-node, and spatial).")
