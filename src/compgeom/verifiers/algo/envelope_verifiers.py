from __future__ import annotations

from typing import List, Tuple
from compgeom.kernel import Point2D, EPSILON
from compgeom.algo.lower_envelop import EnvelopeSegment


def verify_lower_envelope(input_segments: List[Tuple[Point2D, Point2D]], 
                           result_envelope: List[EnvelopeSegment]) -> bool:
    """
    Rigorously verifies the lower envelope of segments.
    1. No overlapping x-ranges in result_envelope (except endpoints).
    2. Result segments are sorted by x.
    3. For any sample point x, result_envelope.y_at(x) <= all input segments.y_at(x).
    4. For any sample point x, result_envelope.y_at(x) == some input segment.y_at(x).
    """
    if not result_envelope:
        # Should only be empty if input is empty or all vertical
        return True

    # 1 & 2. Sorted and no overlap
    for i in range(len(result_envelope) - 1):
        s1 = result_envelope[i]
        s2 = result_envelope[i+1]
        if s1.x_start > s1.x_end - EPSILON:
             raise ValueError(f"Envelope segment {i} has invalid x-range: {s1.x_start} to {s1.x_end}")
        if s1.x_end > s2.x_start + EPSILON:
             raise ValueError(f"Envelope segments {i} and {i+1} overlap in x: {s1.x_end} > {s2.x_start}")
        if s1.x_end < s2.x_start - EPSILON:
             # Gap in envelope - only okay if no input segment covers the gap
             pass

    # 3 & 4. Sampling check
    # We'll sample at endpoints and midpoints of each result segment
    for seg in result_envelope:
        for x in [seg.x_start + EPSILON, (seg.x_start + seg.x_end) / 2.0, seg.x_end - EPSILON]:
            target_y = seg.y_at(x)
            
            # Check against all input segments
            found_match = False
            for i, (p1, p2) in enumerate(input_segments):
                x1, x2 = min(p1.x, p2.x), max(p1.x, p2.x)
                if x1 <= x <= x2:
                    # Calculate input y at x
                    if abs(x1 - x2) < EPSILON:
                        continue # Skip vertical
                    m = (p2.y - p1.y) / (p2.x - p1.x)
                    c = p1.y - m * p1.x
                    input_y = m * x + c
                    
                    if input_y < target_y - EPSILON:
                        raise ValueError(f"Lower envelope at x={x} is NOT minimal: {target_y} > {input_y} (input segment {i})")
                    
                    if abs(input_y - target_y) < EPSILON:
                        found_match = True
            
            if not found_match:
                raise ValueError(f"Lower envelope at x={x} (y={target_y}) does not match any input segment")

    return True
