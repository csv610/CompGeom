"""Sampling helpers for geometric domains."""

from __future__ import annotations

import math
import random

from .geometry import Point


def generate_points_in_circle(center: Point, radius: float, n_points: int = 100):
    points = []
    for index in range(n_points):
        angle = random.uniform(0.0, 2.0 * math.pi)
        distance = radius * math.sqrt(random.random())
        points.append(
            Point(
                center.x + distance * math.cos(angle),
                center.y + distance * math.sin(angle),
                index,
            )
        )
    return points


def generate_points_in_rectangle(width: float, height: float, n_points: int = 100, center: Point | None = None):
    center = center or Point(0.0, 0.0)
    half_width = width / 2.0
    half_height = height / 2.0
    points = []
    for index in range(n_points):
        points.append(
            Point(
                center.x + random.uniform(-half_width, half_width),
                center.y + random.uniform(-half_height, half_height),
                index,
            )
        )
    return points


__all__ = ["generate_points_in_circle", "generate_points_in_rectangle"]
