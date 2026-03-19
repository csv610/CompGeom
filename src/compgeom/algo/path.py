"""Shortest-path routines for planar triangle meshes."""

from __future__ import annotations

import heapq
from collections import defaultdict

from compgeom.kernel import EPSILON, Point2D, contains_point, cross_product, is_on_segment, length, sub
from compgeom.mesh.mesh import mesh_edges


def point_key(point: Point2D):
    return (round(point.x / EPSILON), round(point.y / EPSILON), point.id)


def distance(a: Point2D, b: Point2D) -> float:
    return length(sub(a, b))


def triangle_contains_point(triangle, point: Point2D) -> bool:
    class _TriangleView:
        def __init__(self, vertices):
            self.vertices = vertices

    return contains_point(_TriangleView(triangle), point)


def locate_containing_triangles(triangles, point: Point2D):
    return [index for index, triangle in enumerate(triangles) if triangle_contains_point(triangle, point)]


def point_in_mesh(triangles, point: Point2D) -> bool:
    return bool(locate_containing_triangles(triangles, point))


def build_vertex_map(triangles):
    vertices = {}
    for triangle in triangles:
        for vertex in triangle:
            vertices[vertex.id] = vertex
    return vertices


def build_edge_graph(triangles):
    vertices = build_vertex_map(triangles)
    graph = defaultdict(list)
    for a_id, b_id in mesh_edges(triangles):
        a = vertices[a_id]
        b = vertices[b_id]
        weight = distance(a, b)
        graph[a_id].append((b_id, weight))
        graph[b_id].append((a_id, weight))
    return vertices, graph


def dijkstra(graph, start, goal):
    queue = [(0.0, 0, start)]
    distances = {start: 0.0}
    previous = {}
    sequence = 1

    while queue:
        current_dist, _, node = heapq.heappop(queue)
        if current_dist > distances.get(node, float("inf")) + EPSILON:
            continue
        if node == goal:
            break

        for neighbor, weight in graph.get(node, []):
            candidate = current_dist + weight
            if candidate + EPSILON < distances.get(neighbor, float("inf")):
                distances[neighbor] = candidate
                previous[neighbor] = node
                heapq.heappush(queue, (candidate, sequence, neighbor))
                sequence += 1

    if goal not in distances:
        return None, float("inf")

    path = [goal]
    while path[-1] != start:
        path.append(previous[path[-1]])
    path.reverse()
    return path, distances[goal]


def edge_shortest_path(triangles, source: Point2D, target: Point2D):
    if not point_in_mesh(triangles, source):
        raise ValueError("Source point is outside the mesh.")
    if not point_in_mesh(triangles, target):
        raise ValueError("Target point is outside the mesh.")

    vertices, graph = build_edge_graph(triangles)
    temp_vertices = dict(vertices)
    source_id = "__source__"
    target_id = "__target__"
    temp_vertices[source_id] = source
    temp_vertices[target_id] = target
    graph = defaultdict(list, {node: list(neighbors) for node, neighbors in graph.items()})
    _attach_point_to_edge_graph(triangles, graph, source_id, source)
    _attach_point_to_edge_graph(triangles, graph, target_id, target)

    node_path, total_length = dijkstra(graph, source_id, target_id)
    if node_path is None:
        raise ValueError("No edge path found.")
    return [temp_vertices[node] for node in node_path], total_length


def _attach_point_to_edge_graph(triangles, graph, node_id, point):
    vertices = build_vertex_map(triangles)
    attached = False

    for vertex_id, vertex in vertices.items():
        if point == vertex:
            graph[node_id].append((vertex_id, 0.0))
            graph[vertex_id].append((node_id, 0.0))
            attached = True

    for a_id, b_id in mesh_edges(triangles):
        a = vertices[a_id]
        b = vertices[b_id]
        if not is_on_segment(point, a, b):
            continue
        graph[node_id].append((a_id, distance(point, a)))
        graph[node_id].append((b_id, distance(point, b)))
        graph[a_id].append((node_id, distance(point, a)))
        graph[b_id].append((node_id, distance(point, b)))
        attached = True

    if not attached:
        raise ValueError("Edge mode requires source and target to lie on mesh vertices or edges.")


def boundary_edges(triangles):
    edge_to_triangles = defaultdict(list)
    edge_points = {}
    for triangle_index, triangle in enumerate(triangles):
        a, b, c = triangle
        for start, end in ((a, b), (b, c), (c, a)):
            key = tuple(sorted((start.id, end.id)))
            edge_to_triangles[key].append(triangle_index)
            edge_points[key] = (start, end)
    return [edge_points[key] for key, owners in edge_to_triangles.items() if len(owners) == 1]


def orientation(a: Point2D, b: Point2D, c: Point2D) -> float:
    return cross_product(a, b, c)


def proper_segment_intersection(a: Point2D, b: Point2D, c: Point2D, d: Point2D) -> bool:
    o1 = orientation(a, b, c)
    o2 = orientation(a, b, d)
    o3 = orientation(c, d, a)
    o4 = orientation(c, d, b)

    if abs(o1) <= EPSILON and is_on_segment(c, a, b):
        return False
    if abs(o2) <= EPSILON and is_on_segment(d, a, b):
        return False
    if abs(o3) <= EPSILON and is_on_segment(a, c, d):
        return False
    if abs(o4) <= EPSILON and is_on_segment(b, c, d):
        return False
    return (o1 > EPSILON) != (o2 > EPSILON) and (o3 > EPSILON) != (o4 > EPSILON)


def segment_inside_mesh(triangles, p: Point2D, q: Point2D, mesh_boundary_edges):
    midpoint = Point2D((p.x + q.x) / 2.0, (p.y + q.y) / 2.0)
    if not point_in_mesh(triangles, midpoint) and not any(is_on_segment(midpoint, a, b) for a, b in mesh_boundary_edges):
        return False

    for a, b in mesh_boundary_edges:
        shared_endpoint = p == a or p == b or q == a or q == b
        if shared_endpoint:
            continue
        if proper_segment_intersection(p, q, a, b):
            return False
    return True


def true_shortest_path(triangles, source: Point2D, target: Point2D):
    if not point_in_mesh(triangles, source):
        raise ValueError("Source point is outside the mesh.")
    if not point_in_mesh(triangles, target):
        raise ValueError("Target point is outside the mesh.")

    mesh_boundary = boundary_edges(triangles)
    boundary_vertices = {}
    for start, end in mesh_boundary:
        boundary_vertices[start.id] = start
        boundary_vertices[end.id] = end

    nodes = {"__source__": source, "__target__": target}
    nodes.update({vertex_id: vertex for vertex_id, vertex in boundary_vertices.items()})
    node_ids = list(nodes.keys())

    graph = defaultdict(list)
    for left in range(len(node_ids)):
        for right in range(left + 1, len(node_ids)):
            a_id = node_ids[left]
            b_id = node_ids[right]
            a = nodes[a_id]
            b = nodes[b_id]
            if segment_inside_mesh(triangles, a, b, mesh_boundary):
                weight = distance(a, b)
                graph[a_id].append((b_id, weight))
                graph[b_id].append((a_id, weight))

    node_path, total_length = dijkstra(graph, "__source__", "__target__")
    if node_path is None:
        raise ValueError("No visible path found through the mesh.")
    return [nodes[node] for node in node_path], total_length


def shortest_path(triangles, source: Point2D, target: Point2D, mode: str = "true"):
    mode = mode.lower()
    if mode == "true":
        return true_shortest_path(triangles, source, target)
    if mode == "edges":
        return edge_shortest_path(triangles, source, target)
    raise ValueError(f"Unsupported path mode: {mode}")


__all__ = [
    "boundary_edges",
    "edge_shortest_path",
    "point_in_mesh",
    "shortest_path",
    "true_shortest_path",
]
