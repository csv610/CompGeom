"""Space-filling curve generators."""

from __future__ import annotations

from typing import List, Tuple

from ..geo_math.math_utils import (
    hilbert_index_to_coords,
    morton_index_to_coords,
    peano_index_to_coords,
)


class SpaceFillingCurves:
    """Generators for standard space-filling curves, returning paths as cell indices."""

    @staticmethod
    def peano(level: int) -> List[int]:
        """Generate a Peano curve path as cell indices."""
        width = 3**level
        num_points = 9**level
        indices = []
        for i in range(num_points):
            x, y = peano_index_to_coords(i, level)
            indices.append(y * width + x)
        return indices

    @staticmethod
    def hilbert(order: int) -> List[int]:
        """Generate a Hilbert curve path as cell indices."""
        width = 2**order
        num_points = 4**order
        indices = []
        for i in range(num_points):
            x, y = hilbert_index_to_coords(i, order)
            indices.append(y * width + x)
        return indices

    @staticmethod
    def morton(level: int) -> List[int]:
        """Generate a Morton (Z-order) curve path as cell indices."""
        width = 2**level
        num_points = 4**level
        indices = []
        for i in range(num_points):
            x, y = morton_index_to_coords(i)
            indices.append(y * width + x)
        return indices

    @staticmethod
    def zigzag(width: int, height: int) -> List[int]:
        """Generate a zigzag (boustrophedon-like diagonal) path as cell indices."""
        indices = []
        for diagonal in range(width + height - 1):
            if diagonal % 2 == 0:
                y = min(diagonal, height - 1)
                x = diagonal - y
                while y >= 0 and x < width:
                    indices.append(y * width + x)
                    y -= 1
                    x += 1
            else:
                x = min(diagonal, width - 1)
                y = diagonal - x
                while x >= 0 and y < height:
                    indices.append(y * width + x)
                    x -= 1
                    y += 1
        return indices

    @staticmethod
    def sweep(width: int, height: int) -> List[int]:
        """Generate a snake-like sweep path (row by row) as cell indices."""
        indices = []
        for y in range(height):
            if y % 2 == 0:
                for x in range(width):
                    indices.append(y * width + x)
            else:
                for x in range(width - 1, -1, -1):
                    indices.append(y * width + x)
        return indices

    @staticmethod
    def visualize(indices: List[int], width: int, height: int, cell_size: int = 20) -> str:
        """Return an SVG image string representing the curve path."""
        from ..graphics.visualization import generate_svg_path

        return generate_svg_path(indices, width, height, cell_size)

    @staticmethod
    def save_image(
        indices: List[int], width: int, height: int, filename: str, cell_size: int = 20
    ):
        """Save the curve visualization to a file (SVG or PNG)."""
        from ..graphics.visualization import generate_svg_path, save_png, save_svg

        svg = generate_svg_path(indices, width, height, cell_size)
        if filename.lower().endswith(".png"):
            save_png(svg, filename)
        else:
            save_svg(svg, filename)


__all__ = ["SpaceFillingCurves"]
