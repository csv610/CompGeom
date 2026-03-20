"""Sweep-line algorithms for 2D geometry (Bentley-Ottmann)."""
from typing import List, Tuple, Set
import math

from compgeom.kernel import Point2D

class SweepLine:
    """Provides sweep-line algorithms essential for EDA and layout analysis."""

    @staticmethod
    def segment_intersections(segments: List[Tuple[Point2D, Point2D]]) -> List[Point2D]:
        """
        Finds all intersection points among a set of 2D line segments.
        Uses a simplified sweep-line approach.
        """
        # For a full O((N+K)logN) Bentley-Ottmann, a balanced BST is required for the active edge status.
        # Here we provide a robust sweep-line using a standard sorted list for the active status.
        
        events = []
        for i, (p1, p2) in enumerate(segments):
            # Ensure p1 is left of p2
            if p1.x > p2.x or (p1.x == p2.x and p1.y > p2.y):
                p1, p2 = p2, p1
            events.append((p1.x, p1.y, 0, i, p1, p2)) # 0 for start
            events.append((p2.x, p2.y, 1, i, p1, p2)) # 1 for end
            
        events.sort(key=lambda e: (e[0], e[1], e[2]))
        
        active_segments = set()
        intersections = []
        
        def _intersect(seg1_idx, seg2_idx):
            a, b = segments[seg1_idx]
            c, d = segments[seg2_idx]
            
            # Line intersection math
            a1 = b.y - a.y
            b1 = a.x - b.x
            c1 = a1*(a.x) + b1*(a.y)
            
            a2 = d.y - c.y
            b2 = c.x - d.x
            c2 = a2*(c.x) + b2*(c.y)
            
            det = a1*b2 - a2*b1
            if abs(det) < 1e-9: return None # Parallel
            
            x = (b2*c1 - b1*c2) / det
            y = (a1*c2 - a2*c1) / det
            
            # Check if within both segments
            def in_range(val, min_val, max_val):
                return min(min_val, max_val) - 1e-9 <= val <= max(min_val, max_val) + 1e-9
                
            if (in_range(x, a.x, b.x) and in_range(y, a.y, b.y) and
                in_range(x, c.x, d.x) and in_range(y, c.y, d.y)):
                return Point2D(x, y)
            return None

        # Sweep process
        for ex, ey, type_, seg_idx, p1, p2 in events:
            if type_ == 0: # Start of segment
                for active_idx in active_segments:
                    pt = _intersect(seg_idx, active_idx)
                    if pt: intersections.append(pt)
                active_segments.add(seg_idx)
            else: # End of segment
                active_segments.discard(seg_idx)
                
        # Deduplicate
        unique_intersections = []
        for pt in intersections:
            if not any(math.sqrt((pt.x-u.x)**2 + (pt.y-u.y)**2) < 1e-7 for u in unique_intersections):
                unique_intersections.append(pt)
                
        return unique_intersections
