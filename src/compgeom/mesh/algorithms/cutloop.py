import heapq
from collections import defaultdict, deque


# ======================================
# Mesh
# ======================================

class Mesh:

    def __init__(self, verts, faces):

        self.verts = verts
        self.faces = faces

        self.edges = set()
        self.adj = defaultdict(list)

        self.edge_faces = defaultdict(list)

        for i, (a, b, c) in enumerate(faces):

            self.add_edge(a, b, i)
            self.add_edge(b, c, i)
            self.add_edge(c, a, i)

    def add_edge(self, u, v, f):

        e = tuple(sorted((u, v)))

        self.edges.add(e)

        self.adj[u].append(v)
        self.adj[v].append(u)

        self.edge_faces[e].append(f)


# ======================================
# Euler / genus
# ======================================

def topology(mesh):

    V = len(mesh.verts)
    E = len(mesh.edges)
    F = len(mesh.faces)

    chi = V - E + F

    genus = max(0, (2 - chi) // 2)

    return genus


# ======================================
# primal spanning tree
# ======================================

def primal_tree(mesh):

    parent = {}
    visited = set()

    start = next(iter(mesh.adj))

    stack = [start]

    parent[start] = None

    while stack:

        u = stack.pop()

        if u in visited:
            continue

        visited.add(u)

        for v in mesh.adj[u]:

            if v not in visited:

                parent[v] = u
                stack.append(v)

    tree_edges = set()

    for v, p in parent.items():

        if p is None:
            continue

        tree_edges.add(tuple(sorted((v, p))))

    return tree_edges


# ======================================
# dual graph
# ======================================

def dual_graph(mesh):

    adj = defaultdict(list)

    for e, flist in mesh.edge_faces.items():

        if len(flist) == 2:

            f1, f2 = flist

            adj[f1].append(f2)
            adj[f2].append(f1)

    return adj


# ======================================
# dual spanning tree (cotree)
# ======================================

def dual_tree(mesh):

    adj = dual_graph(mesh)

    visited = set()

    start = next(iter(adj))

    stack = [start]

    tree = set()

    while stack:

        u = stack.pop()

        if u in visited:
            continue

        visited.add(u)

        for v in adj[u]:

            if v not in visited:

                tree.add((u, v))
                stack.append(v)

    return tree


# ======================================
# generator edges
# ======================================

def generator_edges(mesh, tree_edges, dual_tree_edges):

    gens = []

    for e in mesh.edges:

        if e not in tree_edges:

            # if edge not dual-tree
            if len(mesh.edge_faces[e]) == 2:

                f1, f2 = mesh.edge_faces[e]

                if (f1, f2) not in dual_tree_edges and \
                   (f2, f1) not in dual_tree_edges:

                    gens.append(e)

    return gens


# ======================================
# Dijkstra
# ======================================

def edge_length(u, v, verts):

    x1, y1, z1 = verts[u]
    x2, y2, z2 = verts[v]

    return ((x1-x2)**2 +
            (y1-y2)**2 +
            (z1-z2)**2) ** 0.5


def dijkstra(mesh, start):

    dist = {}
    parent = {}

    pq = [(0, start)]

    dist[start] = 0
    parent[start] = None

    while pq:

        d, u = heapq.heappop(pq)

        if d > dist[u]:
            continue

        for v in mesh.adj[u]:

            w = edge_length(u, v, mesh.verts)

            nd = d + w

            if v not in dist or nd < dist[v]:

                dist[v] = nd
                parent[v] = u

                heapq.heappush(pq, (nd, v))

    return parent


# ======================================
# build cycle
# ======================================

def build_path(parent, v):

    path = []

    while v is not None:

        path.append(v)
        v = parent.get(v)

    return path


def generator_cycle(mesh, e):

    u, v = e

    parent = dijkstra(mesh, u)

    path = build_path(parent, v)

    path.append(u)

    return path


# ======================================
# solver
# ======================================

class ShortestCutLoops:

    def __init__(self, verts, faces):

        self.mesh = Mesh(verts, faces)

        self.genus = topology(self.mesh)

        self.tree = primal_tree(self.mesh)

        self.dual = dual_tree(self.mesh)

        self.gens = generator_edges(
            self.mesh,
            self.tree,
            self.dual
        )

    def loop_length(self, loop):

        L = 0

        for i in range(len(loop)-1):

            a = loop[i]
            b = loop[i+1]

            L += edge_length(a, b, self.mesh.verts)

        return L

    def shortest_cut_loops(self):

        loops = []

        for e in self.gens:

            loop = generator_cycle(self.mesh, e)

            L = self.loop_length(loop)

            loops.append((L, loop))

        loops.sort(key=lambda x: x[0])

        needed = max(1, 2 * self.genus)

        return [loop for _, loop in loops[:needed]]
