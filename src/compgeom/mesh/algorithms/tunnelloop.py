import heapq
from collections import defaultdict, deque


# =====================================
# Mesh
# =====================================

class Mesh:

    def __init__(self, verts, faces):

        self.verts = verts
        self.faces = faces

        self.edges = set()
        self.adj = defaultdict(list)

        for a, b, c in faces:

            self.add_edge(a, b)
            self.add_edge(b, c)
            self.add_edge(c, a)

    def add_edge(self, u, v):

        e = tuple(sorted((u, v)))

        if e not in self.edges:

            self.edges.add(e)

            self.adj[u].append(v)
            self.adj[v].append(u)


# =====================================
# Euler characteristic / genus
# =====================================

def topology(mesh):

    V = len(mesh.verts)
    E = len(mesh.edges)
    F = len(mesh.faces)

    chi = V - E + F

    genus = max(0, (2 - chi) // 2)

    return chi, genus


# =====================================
# Spanning tree
# =====================================

def spanning_tree(mesh):

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

    return parent


# =====================================
# Non-tree edges = generators
# =====================================

def generators(mesh, parent):

    tree_edges = set()

    for v, p in parent.items():

        if p is None:
            continue

        tree_edges.add(tuple(sorted((v, p))))

    gens = []

    for e in mesh.edges:

        if e not in tree_edges:
            gens.append(e)

    return gens


# =====================================
# geometry
# =====================================

def edge_length(u, v, verts):

    x1, y1, z1 = verts[u]
    x2, y2, z2 = verts[v]

    return ((x1-x2)**2 +
            (y1-y2)**2 +
            (z1-z2)**2) ** 0.5


# =====================================
# Dijkstra
# =====================================

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

    return dist, parent


# =====================================
# build path
# =====================================

def build_path(parent, v):

    path = []

    while v is not None:

        path.append(v)
        v = parent.get(v)

    return path


# =====================================
# build cycle for generator
# =====================================

def generator_cycle(mesh, e):

    u, v = e

    dist, parent = dijkstra(mesh, u)

    path = build_path(parent, v)

    path.append(u)

    return path


# =====================================
# main solver
# =====================================

class ShortestTunnelSolver:

    def __init__(self, verts, faces):

        self.mesh = Mesh(verts, faces)

        chi, genus = topology(self.mesh)

        self.genus = genus

        self.parent = spanning_tree(self.mesh)

        self.gens = generators(self.mesh, self.parent)

    # --------------------------

    def loop_length(self, loop):

        L = 0

        for i in range(len(loop)-1):

            a = loop[i]
            b = loop[i+1]

            L += edge_length(a, b, self.mesh.verts)

        return L

    # --------------------------

    def shortest_loops(self):

        loops = []

        for e in self.gens:

            loop = generator_cycle(self.mesh, e)

            L = self.loop_length(loop)

            loops.append((L, loop))

        loops.sort(key=lambda x: x[0])

        return loops

    # --------------------------

    def cut_loops(self):

        loops = self.shortest_loops()

        needed = max(1, 2 * self.genus)

        result = []

        for L, loop in loops:

            result.append(loop)

            if len(result) >= needed:
                break

        return result


# =====================================
# example
# =====================================

if __name__ == "__main__":

    verts = [
        (0,0,0),
        (1,0,0),
        (1,1,0),
        (0,1,0),
        (0,0,1),
        (1,0,1),
        (1,1,1),
        (0,1,1),
    ]

    faces = [
        (0,1,2),(0,2,3),
        (4,5,6),(4,6,7),
        (0,1,5),(0,5,4),
        (1,2,6),(1,6,5),
        (2,3,7),(2,7,6),
        (3,0,4),(3,4,7),
    ]

    solver = ShortestTunnelSolver(verts, faces)

    print("Genus:", solver.genus)

    loops = solver.cut_loops()

    for loop in loops:
        print(loop)
