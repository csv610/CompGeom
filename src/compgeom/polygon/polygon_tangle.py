"""Randomize polygon vertex positions within bounding box while preserving topology."""

from __future__ import annotations

import random
from typing import Sequence, Union, TypeVar

from compgeom.kernel import Point2D, Point3D
from compgeom.polygon import Polygon
from compgeom.mesh.mesh_base import Mesh, MeshNode

T = TypeVar("T", Polygon, Mesh)


def tangle_polygon(
    polygon: T,
    seed: int | None = None,
    max_jitter: float = 0.1,
) -> T:
    """Randomize vertex positions within bounding box while preserving topology.

    Args:
        polygon: The input polygon or mesh to tangle.
        seed: Random seed for reproducibility.
        max_jitter: Maximum jitter as fraction of bounding box size (0.0 to 1.0).

    Returns:
        A new Polygon or Mesh with vertices randomized within the bounding box.
    """
    rng = random.Random(seed)

    if isinstance(polygon, Mesh):
        vertices = polygon.vertices
    else:
        vertices = list(polygon.vertices)

    if not vertices:
        return polygon

    min_x = min(p.x for p in vertices)
    max_x = max(p.x for p in vertices)
    min_y = min(p.y for p in vertices)
    max_y = max(p.y for p in vertices)

    width = max_x - min_x
    height = max_y - min_y

    if width < 1e-10 or height < 1e-10:
        return polygon

    jitter_x = width * max_jitter
    jitter_y = height * max_jitter

    new_vertices = []
    for p in vertices:
        new_x = p.x + rng.uniform(-jitter_x, jitter_x)
        new_y = p.y + rng.uniform(-jitter_y, jitter_y)

        new_x = max(min_x, min(max_x, new_x))
        new_y = max(min_y, min(max_y, new_y))

        if isinstance(p, Point3D):
            new_vertices.append(Point3D(new_x, new_y, p.z))
        else:
            new_vertices.append(Point2D(new_x, new_y))

    if isinstance(polygon, Mesh):
        from copy import deepcopy

        new_mesh = deepcopy(polygon)
        new_mesh.nodes = [MeshNode(i, p) for i, p in enumerate(new_vertices)]
        return new_mesh

    return Polygon(new_vertices)
