"""Combinatorial sequences and lower envelopes."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import List, Optional, Tuple, Union

from ..kernel import EPSILON, Point2D


@dataclass
class EnvelopeSegment:
    x_start: float
    x_end: float
    slope: float
    intercept: float
    segment_id: int

    def y_at(self, x: float) -> float:
        return self.slope * x + self.intercept


class DavenportSchinzel:
    """Calculates Davenport-Schinzel sequences for geometric objects."""

    @staticmethod
    def lower_envelope_segments(
        segments: List[Tuple[Point2D, Point2D]]
    ) -> List[EnvelopeSegment]:
        """
        Computes the lower envelope of a set of line segments.
        Returns a list of EnvelopeSegment objects representing the lower envelope.
        """
        if not segments:
            return []

        # Convert input segments to a more usable internal format
        envelope_input = []
        for i, (p1, p2) in enumerate(segments):
            x1, x2 = min(p1.x, p2.x), max(p1.x, p2.x)
            if abs(x1 - x2) < EPSILON:
                # Vertical segment - handle by taking min y at this x
                # (simplified: we mostly care about non-vertical for envelopes)
                continue
            
            # Line equation: y = mx + c
            # slope m = (y2 - y1) / (x2 - x1)
            # intercept c = y1 - m * x1
            if p1.x < p2.x:
                m = (p2.y - p1.y) / (p2.x - p1.x)
                c = p1.y - m * p1.x
            else:
                m = (p1.y - p2.y) / (p1.x - p2.x)
                c = p2.y - m * p2.x
            
            envelope_input.append(EnvelopeSegment(x1, x2, m, c, i))

        return DavenportSchinzel._compute_envelope_recursive(envelope_input)

    @staticmethod
    def _compute_envelope_recursive(
        segments: List[EnvelopeSegment]
    ) -> List[EnvelopeSegment]:
        n = len(segments)
        if n == 0:
            return []
        if n == 1:
            return [segments[0]]

        mid = n // 2
        left_env = DavenportSchinzel._compute_envelope_recursive(segments[:mid])
        right_env = DavenportSchinzel._compute_envelope_recursive(segments[mid:])

        return DavenportSchinzel._merge_envelopes(left_env, right_env)

    @staticmethod
    def _merge_envelopes(
        env1: List[EnvelopeSegment], env2: List[EnvelopeSegment]
    ) -> List[EnvelopeSegment]:
        """Merges two lower envelopes."""
        # Find all critical x-values (endpoints and intersections)
        x_events = set()
        for seg in env1 + env2:
            x_events.add(seg.x_start)
            x_events.add(seg.x_end)

        # Add intersections between segments of env1 and env2
        for s1 in env1:
            for s2 in env2:
                # Intersect y = m1*x + c1 and y = m2*x + c2
                # (m1 - m2)*x = c2 - c1
                dm = s1.slope - s2.slope
                if abs(dm) > 1e-10:
                    ix = (s2.intercept - s1.intercept) / dm
                    # Check if intersection is within both segments' x-ranges
                    if (max(s1.x_start, s2.x_start) - EPSILON <= ix <= 
                        min(s1.x_end, s2.x_end) + EPSILON):
                        x_events.add(ix)

        sorted_x = sorted(list(x_events))
        merged = []

        for i in range(len(sorted_x) - 1):
            x_start = sorted_x[i]
            x_end = sorted_x[i + 1]
            x_mid = (x_start + x_end) / 2.0

            # Find the segment in env1 and env2 that covers this interval
            seg1 = next((s for s in env1 if s.x_start <= x_mid <= s.x_end), None)
            seg2 = next((s for s in env2 if s.x_start <= x_mid <= s.x_end), None)

            best_seg = None
            if seg1 and seg2:
                y1 = seg1.y_at(x_mid)
                y2 = seg2.y_at(x_mid)
                if y1 <= y2:
                    best_seg = seg1
                else:
                    best_seg = seg2
            elif seg1:
                best_seg = seg1
            elif seg2:
                best_seg = seg2

            if best_seg:
                # Add or extend the segment in the merged envelope
                if (merged and merged[-1].segment_id == best_seg.segment_id and 
                    abs(merged[-1].x_end - x_start) < EPSILON):
                    merged[-1].x_end = x_end
                else:
                    merged.append(EnvelopeSegment(
                        x_start, x_end, best_seg.slope, best_seg.intercept, best_seg.segment_id
                    ))

        return merged

    @staticmethod
    def calculate_sequence(segments: List[Tuple[Point2D, Point2D]]) -> List[int]:
        """
        Returns the Davenport-Schinzel sequence (order of segment IDs) 
        for the lower envelope of the given segments.
        """
        envelope = DavenportSchinzel.lower_envelope_segments(segments)
        sequence = []
        for seg in envelope:
            if not sequence or sequence[-1] != seg.segment_id:
                sequence.append(seg.segment_id)
        return sequence


__all__ = ["DavenportSchinzel", "EnvelopeSegment"]
