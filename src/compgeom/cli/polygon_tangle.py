"""Randomize polygon vertex positions within bounding box while preserving topology."""

from __future__ import annotations

import random
from typing import Sequence

from compgeom.kernel import Point2D
from compgeom.polygon import Polygon


def tangle_polygon(
    polygon: Polygon,
    seed: int | None = None,
    max_jitter: float = 0.1,
) -> Polygon:
    """Randomize vertex positions within bounding box while preserving topology.

    Args:
        polygon: The input polygon to tangle.
        seed: Random seed for reproducibility.
        max_jitter: Maximum jitter as fraction of bounding box size (0.0 to 1.0).

    Returns:
        A new Polygon with vertices randomized within the bounding box.
    """
    rng = random.Random(seed)

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

        new_vertices.append(Point2D(new_x, new_y))

    return Polygon(new_vertices)


if __name__ == "__main__":
    poly = Polygon(
        [
            Point2D(0, 0),
            Point2D(4, 0),
            Point2D(4, 3),
            Point2D(0, 3),
        ]
    )

    tangled = tangle_polygon(poly, seed=42, max_jitter=0.2)

    print("Original:")
    for v in poly.vertices:
        print(f"  {v}")

    print("\nTangled:")
    for v in tangled.vertices:
        print(f"  {v}")
