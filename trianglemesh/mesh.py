"""Mesh topology helpers."""

from __future__ import annotations

from collections import defaultdict

from .geometry import Point


def mesh_edges(triangles):
    edges = set()
    for a, b, c in triangles:
        edges.add(tuple(sorted((a.id, b.id))))
        edges.add(tuple(sorted((b.id, c.id))))
        edges.add(tuple(sorted((c.id, a.id))))
    return edges


def mesh_vertices(triangles):
    vertices = {}
    for triangle in triangles:
        for vertex in triangle:
            vertices[vertex.id] = vertex
    return vertices


def euler_characteristic(triangles):
    vertices = mesh_vertices(triangles)
    edges = mesh_edges(triangles)
    faces = len(triangles)
    chi = len(vertices) - len(edges) + faces
    return {
        "vertices": len(vertices),
        "edges": len(edges),
        "faces": faces,
        "euler_characteristic": chi,
    }


def vertex_neighbors(triangles):
    neighbors = defaultdict(set)
    for a, b, c in triangles:
        neighbors[a.id].update([b.id, c.id])
        neighbors[b.id].update([a.id, c.id])
        neighbors[c.id].update([a.id, b.id])
    return {vertex_id: sorted(adjacent) for vertex_id, adjacent in neighbors.items()}


def triangle_neighbors(triangles):
    edge_to_triangles = defaultdict(list)
    for triangle_index, (a, b, c) in enumerate(triangles):
        edge_to_triangles[tuple(sorted((a.id, b.id)))].append(triangle_index)
        edge_to_triangles[tuple(sorted((b.id, c.id)))].append(triangle_index)
        edge_to_triangles[tuple(sorted((c.id, a.id)))].append(triangle_index)

    neighbors = {triangle_index: set() for triangle_index in range(len(triangles))}
    for owners in edge_to_triangles.values():
        if len(owners) != 2:
            continue
        left, right = owners
        neighbors[left].add(right)
        neighbors[right].add(left)
    return {triangle_index: sorted(adjacent) for triangle_index, adjacent in neighbors.items()}


def mesh_neighbors(triangles):
    return {
        "vertex_neighbors": vertex_neighbors(triangles),
        "triangle_neighbors": triangle_neighbors(triangles),
    }


__all__ = [
    "euler_characteristic",
    "mesh_edges",
    "mesh_neighbors",
    "mesh_vertices",
    "triangle_neighbors",
    "vertex_neighbors",
]
