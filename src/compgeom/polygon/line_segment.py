"""Line segment helpers used by polygon algorithms."""

from __future__ import annotations

# Re-exporting from the consolidated kernel module
from ..kernel.line_segment import intersect_proper as proper_segment_intersection, intersect_ray as ray_segment_intersection

__all__ = ["proper_segment_intersection", "ray_segment_intersection"]
