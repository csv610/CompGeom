"""Space-filling curve generators."""

from __future__ import annotations

from typing import List, Tuple

def peano_index_to_coords(index: int, level: int) -> Tuple[int, int]:
    """Convert a Peano curve index to 2D coordinates."""
    x = y = px = py = 0
    for power in range(level - 1, -1, -1):
        power_of_three = 3**power
        digit = (index // (9**power)) % 9
        row = digit // 3
        col = digit % 3 if row % 2 == 0 else 2 - (digit % 3)
        if py % 2 == 1:
            col = 2 - col
        if px % 2 == 1:
            row = 2 - row
        x += col * power_of_three
        y += row * power_of_three
        if col == 1:
            px += 1
        if row == 1:
            py += 1
    return x, y


def morton_index_to_coords(index: int) -> Tuple[int, int]:
    """Convert a Morton curve (Z-order) index to 2D coordinates."""
    x = y = 0
    for bit in range(32):
        x |= (index & (1 << (2 * bit))) >> bit
        y |= (index & (1 << (2 * bit + 1))) >> (bit + 1)
    return x, y


def hilbert_index_to_coords(index: int, order: int) -> Tuple[int, int]:
    """Convert a Hilbert curve index to 2D coordinates."""
    x = y = 0
    t = index
    for scale in range(order):
        rx = 1 & (t // 2)
        ry = 1 & (t ^ rx)
        if ry == 0:
            if rx == 1:
                x, y = (2**scale - 1 - x), (2**scale - 1 - y)
            x, y = y, x
        x += rx * (2**scale)
        y += ry * (2**scale)
        t //= 4
    return x, y

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
