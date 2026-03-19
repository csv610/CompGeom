"""Line segment helpers used by polygon algorithms."""

from __future__ import annotations

from compgeom.kernel.line_segment import intersect_proper as _proper_segment_intersection, intersect_ray as _ray_segment_intersection


def proper_segment_intersection(p1, p2, p3, p4):
    """Checks if segments (p1, p2) and (p3, p4) intersect properly."""
    return _proper_segment_intersection(p1, p2, p3, p4)


def ray_segment_intersection(viewpoint, angle, start, end):
    """Checks if a ray from viewpoint at angle intersects segment (start, end)."""
    return _ray_segment_intersection(viewpoint, angle, start, end)


__all__ = ["proper_segment_intersection", "ray_segment_intersection"]
