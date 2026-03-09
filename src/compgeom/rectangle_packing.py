"""Rectangle packing algorithms for area minimization."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple


@dataclass
class PackedRect:
    x: float
    y: float
    width: float
    height: float
    id: int


class RectanglePacker:
    """Packs rectangles into a minimum area container."""

    @staticmethod
    def pack(
        dimensions: List[Tuple[float, float]], 
        target_shape: str = "rectangle"
    ) -> Tuple[float, float, List[PackedRect]]:
        """
        Packs rectangles into a container.
        
        Args:
            dimensions: List of (width, height) tuples.
            target_shape: "rectangle" or "square".
            
        Returns:
            Tuple of (total_width, total_height, packed_rectangles).
        """
        if not dimensions:
            return 0, 0, []

        # Store original indices to keep track of rectangles
        rects = []
        for i, (w, h) in enumerate(dimensions):
            # Heuristic: orientations can be swapped to improve packing, 
            # but we will keep them as provided for now.
            rects.append({"w": w, "h": h, "id": i})

        # Sort by height descending (Next-Fit Decreasing Height heuristic)
        rects.sort(key=lambda r: r["h"], reverse=True)

        total_area = sum(r["w"] * r["h"] for r in rects)
        max_w = max(r["w"] for r in rects)

        # Heuristic for initial container width
        if target_shape == "square":
            container_width = max(max_w, math.sqrt(total_area))
        else:
            # For rectangle, we start with a slightly wider base to allow for lower height
            container_width = max(max_w, math.sqrt(total_area) * 1.2)

        def attempt_pack(width_limit: float) -> Tuple[float, float, List[PackedRect]]:
            current_x = 0.0
            current_y = 0.0
            shelf_height = 0.0
            max_width_used = 0.0
            placements = []

            for r in rects:
                if current_x + r["w"] > width_limit:
                    # Move to next shelf
                    current_x = 0
                    current_y += shelf_height
                    shelf_height = 0

                placements.append(
                    PackedRect(current_x, current_y, r["w"], r["h"], r["id"])
                )
                current_x += r["w"]
                shelf_height = max(shelf_height, r["h"])
                max_width_used = max(max_width_used, current_x)

            return max_width_used, current_y + shelf_height, placements

        # If square is requested, we try to find a width that makes width ~ height
        if target_shape == "square":
            best_w, best_h, best_placements = attempt_pack(container_width)
            
            # Binary-search-like approach to refine width for squareness
            low = max_w
            high = sum(r["w"] for r in rects)
            
            for _ in range(10): # Iterative refinement
                mid = (low + high) / 2
                w, h, p = attempt_pack(mid)
                
                # If width is much larger than height, try smaller width
                if w > h:
                    high = mid
                else:
                    low = mid
                
                # Keep track of the one with minimum max(w, h)
                if max(w, h) < max(best_w, best_h):
                    best_w, best_h, best_placements = w, h, p
            
            return best_w, best_h, best_placements

        return attempt_pack(container_width)

    @staticmethod
    def visualize(
        width: float, 
        height: float, 
        placements: List[PackedRect], 
        cell_size: int = 20
    ) -> str:
        """Returns an SVG visualization of the packed rectangles."""
        svg_w = width * cell_size
        svg_h = height * cell_size
        
        svg = [
            f'<svg width="{svg_w}" height="{svg_h}" xmlns="http://www.w3.org/2000/svg">',
            '  <rect width="100%" height="100%" fill="white" stroke="black" stroke-width="2" />'
        ]
        
        # Colors for rectangles
        colors = ["#e74c3c", "#3498db", "#2ecc71", "#f1c40f", "#9b59b6", "#1abc9c", "#e67e22"]
        
        for i, r in enumerate(placements):
            color = colors[i % len(colors)]
            # SVG y is from top, our y is from bottom
            y_svg = (height - r.y - r.height) * cell_size
            x_svg = r.x * cell_size
            w_svg = r.width * cell_size
            h_svg = r.height * cell_size
            
            svg.append(
                f'  <rect x="{x_svg}" y="{y_svg}" width="{w_svg}" height="{h_svg}" '
                f'fill="{color}" stroke="black" stroke-width="1" fill-opacity="0.7" />'
            )
            svg.append(
                f'  <text x="{x_svg + w_svg/2}" y="{y_svg + h_svg/2}" '
                f'font-size="12" text-anchor="middle" alignment-baseline="middle">{r.id}</text>'
            )
            
        svg.append("</svg>")
        return "\n".join(svg)


__all__ = ["RectanglePacker", "PackedRect"]
