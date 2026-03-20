from __future__ import annotations
import numpy as np
from typing import List, Tuple, Dict

class UVPacker:
    """
    Implements UV island packing algorithms.
    Shelf Packing algorithm for efficient layout of UV charts.
    """
    @staticmethod
    def pack_islands(island_bounds: List[Tuple[float, float]], margin: float = 0.01) -> List[Tuple[float, float]]:
        """
        Packs UV islands into a unit square [0, 1] x [0, 1].
        island_bounds: List of (width, height) for each island.
        Returns: List of (x, y) coordinates for each island.
        """
        # Sort islands by height (descending) for shelf packing
        indexed_bounds = sorted(enumerate(island_bounds), key=lambda x: x[1][1], reverse=True)
        
        offsets = [None] * len(island_bounds)
        curr_x, curr_y = margin, margin
        row_height = 0
        
        for idx, (w, h) in indexed_bounds:
            # Check if island fits in current row
            if curr_x + w + margin > 1.0:
                # Move to next row
                curr_x = margin
                curr_y += row_height + margin
                row_height = 0
            
            # If it still doesn't fit vertically, we might need to scale everything down
            # (Simplified version: assume it fits or just place it)
            offsets[idx] = (curr_x, curr_y)
            curr_x += w + margin
            row_height = max(row_height, h)
            
        return offsets
